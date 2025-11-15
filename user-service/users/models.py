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
    mfa_type = models.CharField(max_length=10, choices=[('TOTP','TOTP')], blank=True, null=True)
    mfa_secret = models.CharField(max_length=64, blank=True, null=True)


    REQUIRED_FIELDS = ['email']
    
    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        db_table = "users"
        indexes = [models.Index(fields=['role']), models.Index(fields=['email'])]
        ordering = ['username']


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
        db_table = "otp"
        indexes = [models.Index(fields=['user']), models.Index(fields=['code'])]
        ordering = ['-created_at']


# from ast import mod
# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.utils import timezone
# import datetime

# class User(AbstractUser):
#     ROLE_CHOICES = (
#         ('client', 'Client'),
#         ('advocate', 'Advocate'),
#         ('admin', 'Admin'),
#     )
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True)
#     email = models.EmailField(unique=True)
    
#     mfa_enabled = models.BooleanField(default=False)
#     mfa_type = models.CharField(
#         max_length=10,
#         choices=[('TOTP', 'TOTP')],
#         blank=True,
#         null=True
#     )
#     mfa_secret = models.CharField(max_length=64, blank=True, null=True)
    
#     def __str__(self):
#         return f"{self.username} ({self.role})"

#     class Meta:
#         db_table = 'users'
#         indexes = [
#             models.Index(fields=['role']),
#             models.Index(fields=['email']),
#         ]
#         ordering = ['username']


# class ClientProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
#     fullname = models.CharField(max_length=100,blank=True, null=True)
#     phone_number = models.CharField(max_length=12, db_index=True)
#     address = models.TextField()
#     profile_picture = models.ImageField(upload_to='clients/', blank=True, null=True)
    
#     def __str__(self):
#         return self.user.get_full_name() or self.user.username

#     class Meta:
#         db_table = 'client_profile'
#         indexes = [
#             models.Index(fields=['user']),
#             models.Index(fields=['phone_number']),
#         ]


# class AdvocateProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='advocate_profile')
#     phone_number = models.CharField(max_length=12)
#     profile_picture = models.ImageField(upload_to='advocates/', blank=True, null=True)
#     office_address = models.TextField()
#     bar_council_number = models.CharField(max_length=100, unique=True)
#     specialization = models.CharField(max_length=200, db_index=True)
#     years_of_experience = models.IntegerField()
#     educational_qualification = models.CharField(max_length=200)
#     languages = models.CharField(max_length=100, blank=True, null=True)
#     bio = models.TextField()
#     certificates = models.ImageField(upload_to='certificates/',blank=True,null=True)
    
#     def __str__(self):
#         return self.user.get_full_name() or self.user.username

#     class Meta:
#         db_table = 'advocate_profile'
#         indexes = [
#             models.Index(fields=['user']),
#             models.Index(fields=['specialization']),
#         ]


# class OTP(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     code = models.CharField(max_length=6, db_index=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_used = models.BooleanField(default=False, db_index=True)
    
#     def is_expired(self):
#         return timezone.now() > self.created_at + datetime.timedelta(minutes=5)

#     def mark_used(self):
#         self.is_used = True
#         self.save()

#     class Meta:
#         db_table = 'otp'
#         indexes = [
#             models.Index(fields=['user']),
#             models.Index(fields=['code']),
#         ]
#         ordering = ['-created_at']