from django.urls import path
from .views import *
from . import views

app_name = 'management'

urlpatterns = [
    path('', home, name='home'), 
    path('employer/register/', views.employer_register, name='employer_register'),
    path('employer/success/', views.registration_success, name='registration_success'), 
]
