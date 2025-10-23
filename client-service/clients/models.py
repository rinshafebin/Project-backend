from django.db import models
from django.utils import timezone
from users.models import User 


class Case(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("PENDING", "Pending"),
        ("CLOSED", "Closed"),
    ]

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="client_cases",
        limit_choices_to={"role": "client"},
        db_index=True
    )
    advocate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="advocate_cases",
        limit_choices_to={"role": "advocate"},
        db_index=True
    )
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["client"]),
            models.Index(fields=["advocate"]),
            models.Index(fields=["status"]),
            models.Index(fields=["title"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.status})"


class CaseDocument(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="documents")
    file_url = models.CharField(max_length=500)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["case"]),
        ]
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"Document for {self.case.title}"


class HearingDate(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="hearing_dates")
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["case"]),
            models.Index(fields=["date"]),
        ]
        ordering = ["date"]

    def __str__(self):
        return f"Hearing on {self.date} for {self.case.title}"


class Chat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_chats")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_chats")
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="chats", null=True, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["sender", "receiver"]),
            models.Index(fields=["timestamp"]),
        ]
        ordering = ["timestamp"]

    def __str__(self):
        return f"Chat from {self.sender} to {self.receiver}"


class Notification(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        limit_choices_to={"role": "client"},
        db_index=True
    )
    type = models.CharField(max_length=50, db_index=True)
    content = models.TextField()
    read_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["client", "read_status"]),
            models.Index(fields=["type"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification ({self.type}) for {self.client.username}"


class Payment(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments",
        limit_choices_to={"role": "client"},
        db_index=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=[("SUCCESS", "Success"), ("FAILED", "Failed"), ("PENDING", "Pending")],
        default="PENDING"
    )
    invoice = models.CharField(max_length=100, unique=True, db_index=True)
    transaction_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["client"]),
            models.Index(fields=["status"]),
            models.Index(fields=["invoice"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.invoice} ({self.status})"
