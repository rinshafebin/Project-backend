from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import uuid
import mimetypes




class User(AbstractUser):
    role = models.CharField(max_length=20)  
    mfa_enabled = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'
        managed = False  


class ChatRoom(models.Model):
    ROOM_TYPES = [
        ('private', 'Private'),
        ('group', 'Group')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='private')
    participants = models.ManyToManyField(User, related_name='chatrooms')
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(null=True, blank=True)  

    class Meta:
        ordering = ['-last_message_at']

    def __str__(self):
        return self.name


class Message(models.Model):
    MESSAGE_STATUS = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.SET_NULL, null=True)
    content = models.TextField(blank=True)  # blank for file-only messages
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)  # MIME type
    timestamp = models.DateTimeField(default=timezone.now)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    edited = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=MESSAGE_STATUS, default='sent')
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['room', 'timestamp']),
            models.Index(fields=['sender', 'timestamp']),
        ]

    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file.name
            self.file_type, _ = mimetypes.guess_type(self.file.name)
        super().save(*args, **kwargs)

        # Update ChatRoom last_message_at
        self.room.last_message_at = self.timestamp
        self.room.save(update_fields=['last_message_at'])

    def mark_read(self, user):
        self.read_by.add(user)

    def is_read_by(self, user):
        return self.read_by.filter(pk=user.pk).exists()

    def clean(self):
        if not self.content and not self.file:
            raise ValidationError("Message cannot be empty unless a file is attached.")

    def __str__(self):
        sender_name = self.sender.username if self.sender else "Deleted User"
        preview = self.content[:20] + ("..." if len(self.content) > 20 else "")
        return f"{sender_name} @ {self.timestamp}: {preview}"
