from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):  
    role = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'users'
        managed = False  


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
        null=True,
        on_delete=models.SET_NULL,
        related_name='client_cases',
    )
    advocate = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
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
    updated_at = models.DateTimeField(auto_now=True) 
    visible_to_client = models.BooleanField(default=True)  
    visible_to_advocate = models.BooleanField(default=True) 
    
    class Meta:
        db_table = 'case_document'

    def __str__(self):
        return f"Document for {self.case.title}"
    
    
class CaseNote(models.Model):
    case = models.ForeignKey(Case, related_name='notes', on_delete=models.CASCADE)
    note = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'case_note'
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.case.title} by {self.created_by}"
