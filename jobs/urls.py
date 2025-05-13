from django.urls import path
from . import views
from .views import *

app_name = 'jobs'

urlpatterns = [
    path('post_job/', views.post_job, name='post_job'),
    path('job-post-success/', job_post_success, name='job_post_success'),
    path('list/', views.job_list, name='job_list'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('<int:job_id>/apply/', views.apply, name='apply'), 
    path('applications/', views.job_applications_list, name='applications_dashboard'),
    path('applications/<int:application_id>/reply/', views.reply_application, name='reply_application'),
    path('applications/<int:application_id>/delete/', views.delete_application, name='delete_application'),
]