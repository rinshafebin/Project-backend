from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from chat.models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def send_realtime_notification(room_name, sender_id, message_content, file_name=None, file_type=None):
    """
    Sends message to WebSocket group after it is saved in DB
    """
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"chat_{room_name}",
        {
            "type": "chat_message",
            "sender_id": sender_id,
            "message": message_content,
            "file_name": file_name,
            "file_type": file_type
        },
    )
