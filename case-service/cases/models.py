from django.db import models
from django.utils import timezone


class Case(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Pending', 'Pending'),
        ('Closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    RESULT_CHOICES = [
        ('Won', 'Won'),
        ('Lost', 'Lost'),
        ('Pending', 'Pending'),
    ]

    # Case basic fields
    title = models.CharField(max_length=255)
    description = models.TextField()
    case_number = models.CharField(max_length=50, unique=True)

    # Store external service IDs (NOT foreign keys)
    client_id = models.IntegerField(null=True)          # from user-service
    advocate_id = models.IntegerField(null=True)        # from advocate/user-service
    team_id = models.IntegerField(null=True, blank=True) # from advocate-service

    # Case workflow fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='Pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    hearing_date = models.DateField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'case'
    ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.status})"


class CaseTeamMember(models.Model):
    ROLE_CHOICES = [
        ('Lead', 'Lead'),
        ('Junior', 'Junior'),
        ('Reviewer', 'Reviewer'),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='case_team_members')
    user_id = models.IntegerField()  # user-service ID
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Junior')

    class Meta:
        db_table = 'case_team_member'
        unique_together = ('case', 'user_id')

    def __str__(self):
        return f"User {self.user_id} as {self.role} in {self.case.title}"


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

    created_by_id = models.IntegerField(null=True)  # user-service
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'case_note'
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.case.title} by User {self.created_by_id}"
