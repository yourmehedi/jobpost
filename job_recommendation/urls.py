from django.urls import path
from .views import *

app_name = 'job_recommendation'

urlpatterns = [
    path('recommendations/', recommended_jobs, name='recommendations'),
]
