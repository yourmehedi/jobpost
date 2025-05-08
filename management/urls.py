from django.urls import path

from . import views

app_name = 'management'

urlpatterns = [
    path('', views.home, name='home'), 
    path('employer/register/', views.employer_register, name='employer_register'),
    path('employer/success/', views.registration_success, name='registration_success'), 
    path('dashboard/', views.dashboard_home, name='dashboard'),
    path('users/', views.user_approval, name='user_approval'),
    path('management/employers/', views.employer_verification, name='employer_verification'),
    path('jobs/', views.job_monitoring, name='job_monitoring'),
]
