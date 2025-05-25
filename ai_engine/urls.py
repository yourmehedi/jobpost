# ai_engine/urls.py
from django.urls import path
from . import views

app_name = 'ai_engine'

urlpatterns = [
    path('generate-job-description/', views.generate_job_description, name='generate_job_description'),
    path('resume-parser/', views.resume_parser, name='resume_parser'),
]

