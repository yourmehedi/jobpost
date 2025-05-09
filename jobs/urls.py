from django.urls import path
from . import views
from .views import *

app_name = 'jobs'

urlpatterns = [
    path('post_job/', views.post_job, name='post_job'),
    path('list/', views.job_list, name='job_list'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('<int:job_id>/apply/', views.apply, name='apply'), 
    # path('job-list/', job_list, name='job_list'),
    # path('job-detail/<int:pk>/', job_detail, name='job_detail'),
    # path('edit-job/<int:pk>/', edit_job, name='edit_job'),
    # path('delete-job/<int:pk>/', delete_job, name='delete_job'),
]