from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser




class User(AbstractUser):
    role = models.CharField(max_length=20)  

    class Meta:
        db_table = 'users'
        managed = False  




class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    participants = models.ManyToManyField(User, related_name='chatrooms')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True)  # blank for file-only messages
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)  # mime or custom
    timestamp = models.DateTimeField(default=timezone.now)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    edited = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def mark_read(self, user):
        self.read_by.add(user)

    def is_read_by(self, user):
        return self.read_by.filter(pk=user.pk).exists()

    def __str__(self):
        return f"{self.sender} @ {self.timestamp}: {self.content[:20]}"