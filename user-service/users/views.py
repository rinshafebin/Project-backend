import random
import pyotp
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from users.utils import generate_totp_secret, generate_totp_qr


from users.serializers import (
    ClientRegisterSerializer,
    AdvocateRegisterSerializer,
    LoginSerializer,
    ForgetPasswordSerializer,
    ResetPasswordSerializer
)

# ---------------------------------------------------------------------
User = get_user_model()
otp_storage = {}  # Temporary storage (use Redis/DB in production)
# ---------------------------------------------------------------------

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# ---------------------- Client Register ----------------------

class ClientRegisterView(APIView):
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


# ---------------------- Advocate Register ----------------------

class AdvocateRegisterView(APIView):
    def post(self, request):
        serializer = AdvocateRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': "Advocate registered successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------- Login with MFA ----------------------

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # If MFA enabled, ask for verification before issuing tokens
        if user.mfa_enabled:
            return Response({
                'message': "MFA required",
                'mfa_type': user.mfa_type,
                'user_id': user.id
            }, status=status.HTTP_200_OK)

        # Normal login flow
        tokens = get_tokens_for_user(user)
        return Response({
            'message': "Login successful",
            'token': tokens['access'],
            'refresh': tokens['refresh'],
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role
            }
        }, status=status.HTTP_200_OK)


# ---------------------- Forget Password ----------------------

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

        send_mail(
            subject="Your password reset OTP",
            message=(
                f"Hello {user.username},\n\n"
                f"Your OTP for password reset is: {otp}\n"
                f"This OTP will expire soon."
            ),
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
            recipient_list=[email],
            fail_silently=False,
        )

        print(f"Password reset OTP for {email}: {otp}")  # for debugging
        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)


# ---------------------- Reset Password ----------------------

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        if not all([email, otp, new_password]):
            return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

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


# ---------------------- Enable MFA ----------------------

class EnableMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.mfa_enabled:
            return Response({"message": "MFA already enabled"}, status=status.HTTP_400_BAD_REQUEST)

        user.mfa_secret = generate_totp_secret()
        user.mfa_type = 'TOTP'
        user.mfa_enabled = True
        user.save()

        totp = pyotp.TOTP(user.mfa_secret)
        print(f"🔐 MFA OTP for {user.username}: {totp.now()}")

        qr_code = generate_totp_qr(user)
        return Response({
            "message": "MFA Enabled",
            "qr_code": qr_code
        }, status=status.HTTP_200_OK)


# ---------------------- Verify MFA ----------------------

class VerifyMFAView(APIView):
    permission_classes = []  

    def post(self, request):
        user_id = request.data.get("user_id")
        otp_code = request.data.get("otp")

        if not user_id or not otp_code:
            return Response({"error": "Missing user_id or OTP"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(otp_code):
            tokens = get_tokens_for_user(user)
            return Response({
                "message": "MFA verified successfully",
                "token": tokens['access'],
                "refresh": tokens['refresh']
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)



# ------------------------ RequestToOtp  ----------------------

# class RequestOTPView(APIView):
#     def post(self,request):
#         serializer = OTPRequestSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.user
        
#         code = f"{random.randint(100000,999999)}"
        
#         OTP.objects.create(user=user ,code=code)
        
#         input_value = serializer.validated_data['email_or_phone']
#         if '@' in input_value:
#             send_mail(
#                 subject ="OTP for login",
#                 message =f"you OTP code is :{code} ",
#                 from_email='no-reply@myapp.com'
#                 recipient_list=[user.email],
#                 fail_silently=False,
#             ) 
#         else:
#             phone_number = input_value     
    

