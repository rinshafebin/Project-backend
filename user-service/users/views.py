import random
import pyotp 
from django.core.mail import send_mail
from smtplib import SMTPException
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from users.utils import generate_totp_secret, generate_totp_qr
from rest_framework.permissions import AllowAny,IsAuthenticated
from users.serializers import AdvocateProfileUpdateSerializer
from users.models import AdvocateProfile,ClientProfile
from users.serializers import (
    ClientRegisterSerializer,
    AdvocateRegisterSerializer,
    LoginSerializer,
    ForgetPasswordSerializer,
    ResetPasswordSerializer,
    ClientProfileUpdateSerializer,
    AdvocateProfileUpdateSerializer
)

User = get_user_model()
otp_storage = {} 


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# -------------------------------- Client Register --------------------------------

class ClientRegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ClientRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Client registered successfully',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------- Advocate Register -------------------------------

class AdvocateRegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = AdvocateRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': "Advocate registered successfully",
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------- Login --------------------------------

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if user.role in ['admin', 'advocate'] and user.mfa_enabled:
            return Response({
                'message': "MFA required",
                'mfa_type': user.mfa_type,
                'user_id': user.id,
            }, status=status.HTTP_200_OK)

        tokens = get_tokens_for_user(user)
        return Response({
            'message': "Login successful",
            'token': tokens['access'],
            'refresh': tokens['refresh'],
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'mfa_enabled': user.mfa_enabled
            }
        }, status=status.HTTP_200_OK)


# -------------------------------- Google Login -------------------------------

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Google ID token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            email = idinfo.get('email')
            if not email:
                return Response({'error': 'Google token has no email'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'No account associated with this Google account'}, status=status.HTTP_400_BAD_REQUEST)

            tokens = get_tokens_for_user(user)
            return Response({
                'message': 'Login successful via Google',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'role': user.role,
                    'mfa_enabled': user.mfa_enabled
                },
                'token': tokens['access'],
                'refresh': tokens['refresh']
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response({'error': 'Invalid Google token'}, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------- Forget Password --------------------------------

class ForgetPasswordView(APIView):
    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "No user found with that email"}, status=status.HTTP_404_NOT_FOUND)

        otp = str(random.randint(100000, 999999))
        otp_storage[email] = otp
        try:
            send_mail(
                subject="Your password reset OTP",
                message=f"Hello {user.username},\n\nYour OTP for password reset is: {otp}\nThis OTP will expire soon.",
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
                recipient_list=[email],
                fail_silently=False,
            )
        except SMTPException:
            return Response({"error": "Unable to send email right now. Please try again later."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        print(f"[Debug] Password reset OTP for {email}: {otp}")
        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)


# -------------------------------- Reset Password --------------------------------

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        stored_otp = otp_storage.get(email)
        if not stored_otp or stored_otp != otp:
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            del otp_storage[email]
            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


# -------------------------------- Enable MFA --------------------------------

class EnableMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role not in ("admin", "advocate"):
            return Response({"message": "MFA is only available for admin and advocate users."}, status=status.HTTP_403_FORBIDDEN)

        if user.mfa_enabled:
            return Response({"message": "MFA already enabled"}, status=status.HTTP_400_BAD_REQUEST)

        user.mfa_secret = generate_totp_secret()
        user.mfa_type = 'TOTP'
        user.mfa_enabled = True
        user.save()

        qr_code = generate_totp_qr(user)
        return Response({
            "message": "MFA Enabled",
            "qr_code": qr_code
        }, status=status.HTTP_200_OK)


# -------------------------------- Verify MFA --------------------------------

class VerifyMFAView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        otp_code = request.data.get("otp")

        if not user_id or not otp_code:
            return Response({"error": "Missing user_id or OTP"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user.mfa_enabled:
            tokens = get_tokens_for_user(user)
            return Response({
                "message": "Login successful (MFA not required)",
                "token": tokens['access'],
                "refresh": tokens['refresh'],
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "mfa_enabled": user.mfa_enabled
                }
            }, status=status.HTTP_200_OK)

        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(otp_code):
            tokens = get_tokens_for_user(user)
            return Response({
                "message": "MFA verified successfully",
                "token": tokens['access'],
                "refresh": tokens['refresh'],
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "mfa_enabled": user.mfa_enabled
                }
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------- Advocate Profile View --------------------------------

class AdvocateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.advocate_profile
        except AdvocateProfile.DoesNotExist:
            return Response({"success": False, "message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdvocateProfileUpdateSerializer(profile)
        return Response({"success": True, "profile": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request):
        try:
            profile = request.user.advocate_profile
        except AdvocateProfile.DoesNotExist:
            return Response({"success": False, "message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdvocateProfileUpdateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Profile updated successfully", "profile": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------- Client Profile View --------------------------------

class ClientProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.client_profile
        except ClientProfile.DoesNotExist:
            return Response({"success": False, "message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClientProfileUpdateSerializer(profile)
        return Response({"success": True, "profile": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request):
        try:
            profile = request.user.client_profile
        except ClientProfile.DoesNotExist:
            return Response({"success": False, "message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClientProfileUpdateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Profile updated successfully", "profile": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
