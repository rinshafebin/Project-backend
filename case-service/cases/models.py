from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """
    Unmanaged User model - references the users table created by auth-service
    """
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('advocate', 'Advocate'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True)
    email = models.EmailField(unique=True)
    
    mfa_enabled = models.BooleanField(default=False)
    mfa_type = models.CharField(max_length=10, choices=[('TOTP', 'TOTP')], blank=True, null=True)
    mfa_secret = models.CharField(max_length=64, blank=True, null=True)
    
    class Meta:
        db_table = 'users'
        managed = False  # 👈 CRITICAL: Don't manage this table
        
    def __str__(self):
        return f"{self.username} ({self.role})"


class Case(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Pending', 'Pending'),
        ('Closed', 'Closed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    case_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='client_cases',
    )
    advocate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='advocate_cases',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    hearing_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'case'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.status})"


class CaseDocument(models.Model):
    case = models.ForeignKey(Case, related_name='documents', on_delete=models.CASCADE)
    document = models.FileField(upload_to='case_documents/')
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'case_document'

    def __str__(self):
        return f"Document for {self.case.title}"