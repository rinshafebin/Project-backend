from rest_framework import serializers
from .models import ChatRoom, Participant, Message, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']



class ParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Participant
        fields = ['id', 'user', 'role', 'joined_at', 'is_muted', 'is_removed']


class ChatRoomSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)
    total_participants = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'room_type', 'created_at', 'last_message_at', 'participants', 'total_participants']

    def get_total_participants(self, obj):
        return obj.participants.count()



class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    reply_to = serializers.PrimaryKeyRelatedField(queryset=Message.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Message
        fields = [
            'id', 'room', 'sender', 'content', 'file', 'file_name', 'file_type',
            'timestamp', 'status', 'reply_to', 'edited', 'deleted'
        ]
        read_only_fields = ['id', 'timestamp', 'status', 'file_name', 'file_type']

    def validate(self, data):
        if not data.get("content") and not data.get("file"):
            raise serializers.ValidationError("Message must contain text or a file.")
        return data

    def create(self, validated_data):
        """
        Custom create to automatically attach sender from request.user
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['sender'] = request.user
        return super().create(validated_data)
