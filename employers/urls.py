# employer/urls.py
from django.urls import path
from . import views

app_name = 'employers'

urlpatterns = [
    path('employer/register/', views.employer_register, name='employer_register'),
    path('dashboard/', views.employer_dashboard, name='dashboard'),
]
