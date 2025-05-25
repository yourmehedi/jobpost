from django.urls import path
from .views import *

app_name = 'chatbot'

urlpatterns = [
    path('ask/', chatbot_reply, name='chatbot_reply'),
]
