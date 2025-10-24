from django.contrib import admin
from .models import Case, Chat, Notification, Payment

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'advocate', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'client', 'advocate')
    search_fields = ('title', 'description', 'client__username', 'advocate__username')
    ordering = ('-created_at',)


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'case', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('message', 'sender__username', 'receiver__username')
    ordering = ('timestamp',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('client', 'type', 'read_status', 'created_at')
    list_filter = ('type', 'read_status', 'created_at')
    search_fields = ('content', 'client__username')
    ordering = ('-created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'client', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'client')
    search_fields = ('invoice', 'client__username')
    ordering = ('-created_at',)
