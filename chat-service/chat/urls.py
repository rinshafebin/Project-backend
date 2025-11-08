from django.urls import path
from .views import ChatRoomListCreateView, ChatRoomDetailView, MessageListCreateView, MessageDetailView

urlpatterns = [
    path('chatrooms/', ChatRoomListCreateView.as_view(), name='chatroom-list-create'),
    path('chatrooms/<uuid:pk>/', ChatRoomDetailView.as_view(), name='chatroom-detail'),
    path('chatrooms/<uuid:room_id>/messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<uuid:pk>/', MessageDetailView.as_view(), name='message-detail'),
]
