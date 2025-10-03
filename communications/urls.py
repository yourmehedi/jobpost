from django.urls import path
from . import views

app_name = 'communications'


urlpatterns = [
    path('compose/', views.compose_message, name='compose_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('broadcast/', views.broadcast_create, name='broadcast_create'),
]
