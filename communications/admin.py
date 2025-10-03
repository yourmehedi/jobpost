from django.contrib import admin
from .models import Message, Notification, Broadcast

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject','sender','recipient','sent_at','is_read','is_broadcast')
    search_fields = ('subject','body','sender__username','recipient__username')
    list_filter = ('is_read', 'is_broadcast', 'sent_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title','user','is_read','created_at','target_role')
    search_fields = ('title','message','user__username')
    list_filter = ('is_read', 'target_role', 'created_at')


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ('subject','sender','target_role','created_at')
    filter_horizontal = ('recipients',)
