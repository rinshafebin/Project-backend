from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from chat.models import ChatRoom, Message, Participant
from chat.serializers import ChatRoomSerializer, MessageSerializer
from chat.permissions import IsAuthenticatedViaUserService


class ChatRoomListCreateView(APIView):
    permission_classes = [IsAuthenticatedViaUserService]

    def get(self, request):
        user_id = request.user_data["id"]
        chatrooms = ChatRoom.objects.filter(participants__user_id=user_id)
        serializer = ChatRoomSerializer(chatrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ChatRoomSerializer(data=request.data)
        if serializer.is_valid():
            chatroom = serializer.save()
            Participant.objects.create(chatroom=chatroom, user_id=request.user_data["id"], role="creator")
            return Response(ChatRoomSerializer(chatroom).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatRoomDetailView(APIView):
    permission_classes = [IsAuthenticatedViaUserService]

    def get(self, request, pk):
        user_id = request.user_data["id"]
        chatroom = get_object_or_404(ChatRoom, pk=pk, participants__user_id=user_id)
        serializer = ChatRoomSerializer(chatroom)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageListCreateView(APIView):
    permission_classes = [IsAuthenticatedViaUserService]

    def get(self, request, room_id):
        user_id = request.user_data["id"]
        chatroom = get_object_or_404(ChatRoom, id=room_id, participants__user_id=user_id)
        messages = Message.objects.filter(room=chatroom).order_by("timestamp")
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, room_id):
        user_id = request.user_data["id"]
        chatroom = get_object_or_404(ChatRoom, id=room_id, participants__user_id=user_id)
        serializer = MessageSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(room=chatroom, sender_id=user_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageDetailView(APIView):
    permission_classes = [IsAuthenticatedViaUserService]

    def patch(self, request, pk):
        user_id = request.user_data["id"]
        message = get_object_or_404(Message, pk=pk, sender_id=user_id)
        serializer = MessageSerializer(message, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save(edited=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user_id = request.user_data["id"]
        message = get_object_or_404(Message, pk=pk, sender_id=user_id)
        message.deleted = True
        message.save(update_fields=["deleted"])
        return Response({"detail": "Message deleted"}, status=status.HTTP_204_NO_CONTENT)


class MarkMessageReadView(APIView):
    permission_classes = [IsAuthenticatedViaUserService]

    def post(self, request, pk):
        user_id = request.user_data["id"]
        message = get_object_or_404(Message, pk=pk)
        message.read_by.add(user_id)
        return Response({"detail": "Message marked as read."}, status=status.HTTP_200_OK)
