# ai_engine/urls.py

from django.urls import path
from . import views

app_name = 'ai_engine'

urlpatterns = [
    path('resume-parse/', views.resume_parser, name='resume_parse'),
]
