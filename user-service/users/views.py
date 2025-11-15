import random
import pyotp
from smtplib import SMTPException

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from users.utils import generate_totp_secret, generate_totp_qr
from users.serializers import (
    ClientRegisterSerializer,
    AdvocateRegisterSerializer,
    LoginSerializer,
    ForgetPasswordSerializer,
    ResetPasswordSerializer,
)

from .tasks import send_welcome_email, emit_user_created_event

User = get_user_model()
otp_storage = {}   


# -------------------------- TOKEN GENERATOR -------------------------- #

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


# ---------------------------- REGISTER VIEWS ---------------------------- #

class ClientRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClientRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        send_welcome_email.delay(user.email, user.username)

        emit_user_created_event(user.id, role="client", profile_payload=None)

        return Response({"message": "Client registered"}, status=status.HTTP_201_CREATED)


class AdvocateRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdvocateRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        profile_data = getattr(user, "_initial_profile_data", None)

        send_welcome_email.delay(user.email, user.username)
        emit_user_created_event(user.id, role="advocate", profile_payload=profile_data)

        return Response({"message": "Advocate registered"}, status=status.HTTP_201_CREATED)


# ----------------------------- LOGIN VIEWS ----------------------------- #

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        if user.role in ["admin", "advocate"] and user.mfa_enabled:
            return Response({
                "message": "MFA required",
                "mfa_type": user.mfa_type,
                "user_id": user.id
            }, status=status.HTTP_200_OK)

        tokens = get_tokens_for_user(user)
        return Response({
            "message": "Login successful",
            "token": tokens["access"],
            "refresh": tokens["refresh"],
            "user": {"id": user.id, "email": user.email, "role": user.role, "mfa_enabled": user.mfa_enabled}
        })


# --------------------------- GOOGLE LOGIN --------------------------- #

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Google token required"}, status=400)

        try:
            info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
        except ValueError:
            return Response({"error": "Invalid Google token"}, status=400)

        email = info.get("email")
        if not email:
            return Response({"error": "Google account has no email"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "No account found for this email"}, status=404)

        tokens = get_tokens_for_user(user)
        return Response({
            "message": "Google login successful",
            "token": tokens["access"],
            "refresh": tokens["refresh"],
            "user": {"id": user.id, "email": user.email, "role": user.role}
        })


# --------------------------- FORGET PASSWORD --------------------------- #

class ForgetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "No user found"}, status=404)

        otp = str(random.randint(100000, 999999))
        otp_storage[email] = otp

        try:
            send_mail(
                subject="Your password reset OTP",
                message=f"Your OTP: {otp}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except SMTPException:
            return Response({"error": "Email service unavailable"}, status=503)

        return Response({"message": "OTP sent"}, status=200)


# --------------------------- RESET PASSWORD --------------------------- #

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        stored_otp = otp_storage.get(email)

        if not stored_otp or stored_otp != otp:
            return Response({"error": "Invalid OTP"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        user.set_password(new_password)
        user.save()
        del otp_storage[email]

        return Response({"message": "Password reset successful"}, status=200)


# ------------------------------ MFA ENABLE ------------------------------ #

class EnableMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.role not in ("admin", "advocate"):
            return Response({"message": "MFA allowed only for admin/advocate"}, status=403)

        if user.mfa_enabled:
            return Response({"message": "MFA already enabled"}, status=400)

        user.mfa_secret = generate_totp_secret()
        user.mfa_type = "TOTP"
        user.mfa_enabled = True
        user.save()

        qr_code = generate_totp_qr(user)

        return Response({
            "message": "MFA Enabled",
            "qr_code": qr_code
        })


# ------------------------------ MFA VERIFY ------------------------------ #

class VerifyMFAView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get("user_id")
        otp = request.data.get("otp")

        if not user_id or not otp:
            return Response({"error": "Missing fields"}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if not user.mfa_enabled:
            tokens = get_tokens_for_user(user)
            return Response({
                "message": "Login successful",
                "token": tokens["access"],
                "refresh": tokens["refresh"]
            })

        totp = pyotp.TOTP(user.mfa_secret)

        if not totp.verify(otp):
            return Response({"error": "Invalid OTP"}, status=400)

        # MFA passed → issue token
        tokens = get_tokens_for_user(user)
        return Response({
            "message": "MFA verified",
            "token": tokens["access"],
            "refresh": tokens["refresh"]
        })


# --------------------------- TOKEN VALIDATION --------------------------- #

class ValidateTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "valid": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        })
