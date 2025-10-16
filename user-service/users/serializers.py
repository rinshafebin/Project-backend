from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from users.models import ClientProfile,AdvocateProfile
from django.db.models import Q
import re

User =get_user_model()



# -------------------------------- Client Register Serializer -------------------------------

class ClientRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True,required=True,validators=[validate_password])
    confirm_password = serializers.CharField(write_only = True,required=True)
    
    class Meta:
        model = User
        fields = ('username','email','password','confirm_password','role')
        
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password ": "Password fields didn't match."})
        if data['role'] != 'client':
            raise serializers.ValidationError({"role":"Role must be client"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user =User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role = 'client'
        )
        ClientProfile.objects.create(user=user)
        return user
    


    
# -------------------------------- Advocate Register Serializer -------------------------------


class AdvocateRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=True,validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True,required=True)
    
    phone_number = serializers.CharField(required=True)
    office_address = serializers.CharField(required=True)
    bar_council_number = serializers.CharField(required=True)
    specialization = serializers.CharField(required=True)
    years_of_experience = serializers.IntegerField(required=True)
    educational_qualification = serializers.CharField(required=True)
    languages  = serializers.CharField(required=True)
    bio = serializers.CharField(required=True)
    profile_picture = serializers.ImageField(required=False,allow_null=True)
    
    
    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'confirm_password', 'role',
            'phone_number', 'office_address', 'bar_council_number',
            'specialization', 'years_of_experience', 'educational_qualification',
            'languages', 'bio', 'profile_picture'
        )
        
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password" : "password fields didn't match"})
        if data['role'] != 'advocate':
            raise serializers.ValidationError({"role":"Role must be advocate"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')   
        
        profile_data = {
            'phone_number': validated_data.pop('phone_number'),
            'office_address': validated_data.pop('office_address'),
            'bar_council_number': validated_data.pop('bar_council_number'),
            'specialization': validated_data.pop('specialization'),
            'years_of_experience': validated_data.pop('years_of_experience'),
            'educational_qualification': validated_data.pop('educational_qualification'),
            'languages': validated_data.pop('languages', ''),
            'bio': validated_data.pop('bio'),
            'profile_picture': validated_data.pop('profile_picture', None),
        }
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email = validated_data['email'],
            password= validated_data['password'],
            role = 'advocate'  
        )
        
        AdvocateProfile.objects.create(user=user,**profile_data)
        return user
    
    
# -------------------------------- login Serializer with password -------------------------------
 
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required =True)
    password = serializers.CharField(write_only=True,required=True)
    
    def validate(self,data):
        email = data.get('email')
        password = data.get('password')
        
        try:
            user =User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'details : "invalid Credentials'})
         
        
        if not user.check_password(password):
            raise serializers.ValidationError({'deatail' :"invalid credentials"})
        
        data['user'] =user
        return data


# -------------------------------- loginSerializerWithOtp -------------------------------

# class OTPRequestSerializer(serializers.Serializer):
#     email_or_phone = serializers.CharField(required=True)
    
#     def validate_email_or_phone(self,value):
#         user = None
#         if '@' in value:
#             user = User.objects.filter(email=value).first()
#         else :
#             user =User.objects.filter(
#                 Q(client_profile__phone_number=value)|
#                 Q(advocate_profile__phone_number=value)
                
#             ).first()
            
#         if not user:
#             raise serializers.ValidationError("user not found with this email/phone")
        
#         self.user = user
#         return value


# -------------------------------- ForgetPasswordSerializer -------------------------------

class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email")
        return value
    


# -------------------------------- ResetPasswordSerializer -------------------------------

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True,min_length=6)


    def validate_new_password(self, value):
        if not re.search(r'[A-Z]',value):
            raise serializers.ValidationError("Password must contain at least 1 uppercase letter.")
        if not re.search(r'[a-z]',value):
            raise serializers.ValidationError("Password must contain at least 1 lowercase letter.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least 1 digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least 1 special character.")
        return value
    
    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be numeric")
        if len(value)!=6:
            raise serializers.ValidationError("OTP must be 6 digits")
        return value