# employer/urls.py
from django.urls import path
from . import views

app_name = 'employers'

urlpatterns = [
    path('dashboard/', views.employer_dashboard, name='dashboard'),
]
