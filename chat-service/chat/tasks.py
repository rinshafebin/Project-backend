from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@shared_task
def send_realtime_notification(room_name, sender_id, message):
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"chat_{room_name}",
        {
            "type": "chat_message",
            "sender_id": sender_id,
            "message": message,
        },
    )
