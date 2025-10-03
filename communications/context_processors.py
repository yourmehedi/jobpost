from .models import Notification
from django.utils import timezone

def unread_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    else:
        notifications = []
    return {
        'notifications_dropdown': notifications
    }
