from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.serializers import ClientRegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore
from users.serializers import AdvocateRegisterSerializer,LoginSerializer,ForgetPasswordSerializer,ResetPasswordSerializer
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
import random


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
