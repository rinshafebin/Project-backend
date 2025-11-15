from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import datetime


class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('advocate', 'Advocate'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True)
    email = models.EmailField(unique=True)

    mfa_enabled = models.BooleanField(default=False)
    mfa_type = models.CharField(
        max_length=10,
        choices=[('TOTP', 'TOTP')],
        blank=True,
        null=True
    )
    mfa_secret = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email']),
        ]
        ordering = ['username']


class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    full_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, db_index=True, blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    state = models.CharField(max_length=120, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to='clients/', blank=True, null=True)

    def __str__(self):
        return self.full_name or self.user.username

    class Meta:
        db_table = 'client_profile'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['phone']),
        ]


class AdvocateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="advocate_profile")
    
    # Personal info
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    
    # Professional info
    bar_council_id = models.CharField(max_length=100, unique=True)
    enrollment_year = models.IntegerField(blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    languages = models.CharField(max_length=255, blank=True, null=True)  # comma separated
    specializations = models.ManyToManyField(Specialization, related_name="advocates", blank=True)
    
    # Address info
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    state = models.CharField(max_length=120, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    
    # Profile info
    profile_image = models.ImageField(upload_to="advocates/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    rating = models.FloatField(default=0.0)
    cases_count = models.IntegerField(default=0)
    wins_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name or self.user.username

    class Meta:
        db_table = 'advocate_profile'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['bar_council_id']),
            models.Index(fields=['full_name']),
        ]
        ordering = ['full_name']


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False, db_index=True)

    def is_expired(self):
        return timezone.now() > self.created_at + datetime.timedelta(minutes=5)

    def mark_used(self):
        self.is_used = True
        self.save()

    class Meta:
        db_table = 'otp'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['code']),
        ]
        ordering = ['-created_at']
