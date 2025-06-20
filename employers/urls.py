# employer/urls.py
from django.urls import path
from . import views

app_name = 'employers'

urlpatterns = [
    path('dashboard/', views.employer_dashboard, name='dashboard'),
    path('edit_profile/', views.edit_employer_profile, name='edit_profile'),
    path('settings/', views.employer_settings, name='settings'),
    path('telegram-settings/', views.telegram_settings, name='telegram_settings'),
]
