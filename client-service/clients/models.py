from django.db import models
from django.utils import timezone


class User(models.Model):
    
    class Meta:
        db_table = 'users'   # Table name from auth service
        managed = False      # Do NOT create migrations for this table


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
        db_table = 'case'
        indexes = [
            models.Index(fields=["client"]),
            models.Index(fields=["advocate"]),
            models.Index(fields=["status"]),
            models.Index(fields=["title"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.status})"


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
        db_table = 'payment'
        indexes = [
            models.Index(fields=["client"]),
            models.Index(fields=["status"]),
            models.Index(fields=["invoice"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.invoice} ({self.status})"



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
        db_table = 'notification'
        indexes = [
            models.Index(fields=["client", "read_status"]),
            models.Index(fields=["type"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification ({self.type}) for {self.client_id}"
