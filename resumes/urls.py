from django.urls import path
from . import views

app_name = 'resumes'

urlpatterns = [
    path('upload/', views.upload_resume, name='resume_upload'),
    path('list/', views.resume_list, name='resume_list'),
]
