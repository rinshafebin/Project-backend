from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from chat.models import ChatRoom, Message, Participant
from chat.serializers import ChatRoomSerializer, MessageSerializer


class ChatRoomListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        chatrooms = ChatRoom.objects.filter(participants__user=request.user)
        serializer = ChatRoomSerializer(chatrooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ChatRoomSerializer(data=request.data)
        if serializer.is_valid():
            chatroom = serializer.save()
            Participant.objects.create(chatroom=chatroom, user=request.user, role='creator')
            return Response(ChatRoomSerializer(chatroom).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatRoomDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        chatroom = get_object_or_404(ChatRoom, pk=pk, participants__user=request.user)
        serializer = ChatRoomSerializer(chatroom)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, room_id):
        chatroom = get_object_or_404(ChatRoom, id=room_id, participants__user=request.user)
        messages = Message.objects.filter(room=chatroom).order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, room_id):
        chatroom = get_object_or_404(ChatRoom, id=room_id, participants__user=request.user)
        serializer = MessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(room=chatroom)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        message = get_object_or_404(Message, pk=pk, sender=request.user)
        serializer = MessageSerializer(message, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save(edited=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        message = get_object_or_404(Message, pk=pk, sender=request.user)
        message.deleted = True
        message.save(update_fields=['deleted'])
        return Response({"detail": "Message deleted"}, status=status.HTTP_204_NO_CONTENT)


class MarkMessageReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        message = get_object_or_404(Message, pk=pk)
        message.read_by.add(request.user)
        return Response({"detail": "Message marked as read."}, status=status.HTTP_200_OK)
