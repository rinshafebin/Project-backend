from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import ClientProfile, AdvocateProfile, Specialization
from datetime import date

User = get_user_model()



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        if not value.isalnum():
            raise serializers.ValidationError("Username must be alphanumeric")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters")
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("Password must contain at least one number")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            role='client'
        )
        ClientProfile.objects.create(user=user)
        return user



class AdvocateRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    bar_council_id = serializers.CharField(
        validators=[RegexValidator(r'^[A-Za-z0-9]+$', 'Bar council ID must be alphanumeric')]
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'bar_council_id']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        if not value.isalnum():
            raise serializers.ValidationError("Username must be alphanumeric")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters")
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("Password must contain at least one number")
        return value

    def validate_bar_council_id(self, value):
        if AdvocateProfile.objects.filter(bar_council_id=value).exists():
            raise serializers.ValidationError("Bar council ID already exists")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        bar_council_id = validated_data.pop('bar_council_id')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            role='advocate'
        )
        AdvocateProfile.objects.create(user=user, bar_council_id=bar_council_id)
        return user



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid username or password")
        data['user'] = user
        return data



class ClientProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False)

    class Meta:
        model = ClientProfile
        fields = ['full_name', 'phone_number', 'address', 'profile_picture']

    def validate_phone_number(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits")
        if value and len(value) < 7:
            raise serializers.ValidationError("Phone number is too short")
        return value

    def validate_full_name(self, value):
        if value and len(value) < 3:
            raise serializers.ValidationError("Full name is too short")
        return value



class AdvocateProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False)
    specializations = serializers.ListField(
        child=serializers.CharField(), required=False
    )

    class Meta:
        model = AdvocateProfile
        fields = [
            'full_name', 'phone_number', 'gender', 'dob', 'office_address',
            'specializations', 'years_of_experience', 'educational_qualification',
            'languages', 'bio', 'certificates', 'profile_picture'
        ]

    def validate_phone_number(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits")
        if value and len(value) < 7:
            raise serializers.ValidationError("Phone number is too short")
        return value

    def validate_full_name(self, value):
        if value and len(value) < 3:
            raise serializers.ValidationError("Full name is too short")
        return value

    def validate_dob(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future")
        return value

    def validate_years_of_experience(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Years of experience cannot be negative")
        return value

    def update(self, instance, validated_data):
        specializations = validated_data.pop('specializations', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if specializations:
            for name in specializations:
                spec, _ = Specialization.objects.get_or_create(name=name)
                instance.specializations.add(spec)
        return instance


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters")
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("Password must contain at least one number")
        return value
