from email import message
from django.db.models.signals import post_save
from django.dispatch import receiver
from chat.models import Message
from chat.tasks import send_realtime_notification

@receiver(post_save,sender=Message)
def handle_new_messages(sender,instance,created,**kwargs):
    if created:
        send_realtime_notification.delay(
            room_name = instance.room_name,
            sender_id = instance.sender.id,
            message = instance.content
        )