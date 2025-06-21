from django.urls import path
from . import views

app_name = 'resumes'

urlpatterns = [
    path('upload/', views.upload_resume, name='resume_upload'),
    path('list/', views.resume_list, name='resume_list'),
    path('upload/success/', views.resume_success, name='resume_success'),
    path('jobseeker/<int:user_id>/resumes/', views.jobseeker_resume_list, name='jobseeker_resume_list'),
    path('resume/<int:resume_id>/delete/', views.delete_resume, name='delete_resume'),
]
