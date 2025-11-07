import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # Join the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"✅ Connected to room {self.room_name}")

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"❌ Disconnected from room {self.room_name}")

    async def receive(self, text_data):
        """
        Just broadcast received messages to WebSocket group.
        Message saving is handled asynchronously by Celery.
        """
        data = json.loads(text_data)
        message = data.get("message")
        sender_id = data.get("sender_id")
        file_name = data.get("file_name")
        file_type = data.get("file_type")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender_id": sender_id,
                "file_name": file_name,
                "file_type": file_type
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender_id": event["sender_id"],
            "file_name": event.get("file_name"),
            "file_type": event.get("file_type")
        }))
