from django.urls import path

from . import views

app_name = 'management'

urlpatterns = [
    path('', views.home, name='home'), 
    path('employer/register/', views.employer_register, name='employer_register'),
     path('employer/register/success/', views.registration_success, name='registration_success'), 
    path('jobportal-admin_dashboard/', views.dashboard_home, name='dashboard'),
    path('users/', views.user_approval, name='user_approval'),
    path('verify-employer/<int:id>/', views.verify_employer, name='verify_employer'),
    path('management/employers/', views.employer_verification, name='employer_verification'),
    path('superuser-login/', views.superuser_login_view, name='superuser_login'),
    path('job-monitoring/', views.job_monitoring, name='job_monitoring'),
    path('review-user-jobs/<int:employer_id>/', views.review_user_jobs, name='review_user_jobs'),
    path('toggle-job-status/<int:job_id>/', views.toggle_job_status, name='toggle_job_status'),
    path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),

]
