from django.urls import path
from .views import *
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('reply/', views.chatbot_reply, name='chatbot_reply'),
]
