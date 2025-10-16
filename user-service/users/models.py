from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import datetime

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES =(
        ('client','Client'),
        ('advocate','Advocate'),     
    )
    role= models.CharField(max_length=20,choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    

class ClientProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='client_profile')
    phone_number = models.CharField(max_length=12)
    address = models.TextField()
    profile_picture = models.ImageField(upload_to='clients/',blank=True,null=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username

    
class AdvocateProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='advocate_profile')
    phone_number = models.CharField(max_length=12)
    profile_picture = models.ImageField(upload_to='advocates/',blank=True,null=True)
    office_address = models.TextField()
    bar_council_number = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200)
    years_of_experience = models.IntegerField()
    educational_qualification = models.CharField(max_length=200)
    languages = models.CharField(max_length=100,blank=True,null=True)
    bio = models.TextField()
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    
class AdvocateCase(models.Model):
    advocate = models.ForeignKey(AdvocateProfile, on_delete=models.CASCADE, related_name='cases')
    title = models.CharField(max_length=255)
    case_type = models.CharField(max_length=50)  
    court = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=50)  
    description = models.TextField()
    role_in_case = models.CharField(max_length=50)  
    key_achievements = models.TextField()
    
    def __str__(self):
        return f"{self.title} ({self.status})"


class OTP(models.Model):
    user = models.ForeignKey('users.User',on_delete=models.CASCADE)
    code =models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def is_expired(self):
        return timezone.now() >self.created_at + datetime.timedelta(minutes=5)

