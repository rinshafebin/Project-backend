import random
import pyotp 
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from users.serializers import ClientRegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken  
from rest_framework.permissions import IsAuthenticated
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from users.utils import generate_totp_secret, generate_totp_uri, generate_totp_qr
from users.serializers import (
    AdvocateRegisterSerializer,
    LoginSerializer,
    ForgetPasswordSerializer,
    ResetPasswordSerializer)

# Create your views here.
User = get_user_model()

otp_storage={}

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh':str(refresh),
        'access':str(refresh.access_token),
    }


# -------------------------------- ClientRegisterView  -------------------------------

class ClientRegisterView(APIView):
    def post(self,request):
        serializer = ClientRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message':'Client registered successfully',
                'user':{
                    'username' : user.username,
                    'email' : user.email,
                    'role':user.role
                }
            },status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



# -------------------------------- AdvocateRegisterView  -------------------------------

class AdvocateRegisterView(APIView):
    def post(self,request):
        serializer = AdvocateRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {'message' :"Advocate registered successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


# ------------------------ LoginView with password  ---------------------
  
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
    
        # FOR CHECKING
        tokens = get_tokens_for_user(user)

        
        if user.mfa_enabled:
            return Response({
                'message':"MFA required",
                'mfa_type':user.mfa_type,
                'user_id': user.id,
                'tokens': tokens

            },status = status.HTTP_200_OK
            )
                 
        tokens = get_tokens_for_user(user)

        return Response(
            {
                'message': "Login successfully",
                'tokens': tokens
            },
            status=status.HTTP_200_OK
        )



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
    

# ------------------------ ForgetPasswordView  ----------------------

class ForgetPasswordView(APIView):
    def post(self,request):
        serializer = ForgetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        email =serializer.validated_data["email"]
        user = User.objects.get(email=email)
        
        otp = str(random.randint(100000,999999))
        otp_storage[email]=otp
        
        send_mail(
            subject = "Your password reset OTP",
            message=f"hello { user.username},\n\nYour OTP for password reset is :{otp}\n\n this OTP will expire soon.",
            from_email="rinshafebinkk12@gmail.com",
            recipient_list=[email],
            fail_silently=False,
            
        )
        print(otp)
        return Response({"message":"OTP sent to your email"},status=status.HTTP_200_OK)
    
    
    
# ------------------------ ResetPasswordView  ----------------------

class ResetPasswordView(APIView):
    def post(self,request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data["email"]
        otp =serializer.validated_data['otp']
        new_password =serializer.validated_data['new_password']
        
        if not all([email, otp, new_password]):
            return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)
        
        stored_otp = otp_storage.get(email)
        if not stored_otp or stored_otp !=otp:
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            user =User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            del otp_storage[email]
            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)




# ------------------------ MFAAuthenticatonEnable  ----------------------

class EnableMFAView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        user = request.user
        
        if user.mfa_enabled:
            return Response({"message":"MFA already enabled"},status=400)
        
        user.mfa_secret = generate_totp_secret()
        user.mfa_type = 'TOTP'
        user.mfa_enabled = True
        user.save()
        
        #for printing
        totp = pyotp.TOTP(user.mfa_secret)
        current_otp = totp.now()  
        print(f"🔐 MFA OTP for {user.username}: {current_otp}") 
        
        qr_code = generate_totp_qr(user)
        
        return Response({
            "message":"MFA Enabled",
            "qr_code": qr_code
        })

# ------------------------ MFAAuthenticatonVerify  ----------------------

class VerifyMFAview(APIView):
    permission_classes =[IsAuthenticated]
    
    def post(self,request):
        user_id = request.data.get("user_id")
        otp_code = request.data.get("otp")
        
        if not user_id or not otp_code:
            return Response({"error": "Missing user_id or OTP"}, status=400)

        try:
            user =User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error":"user not found"},status=400)
        print(user_id)
        
        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(otp_code):
            tokens = get_tokens_for_user(user)
            return Response({
                 "message": "MFA verified successfully",
                "tokens": tokens
            })
        else:
            return Response({"error": "Invalid OTP"}, status=400)

