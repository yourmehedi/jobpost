from django.urls import path
from . import views

app_name = 'jobseeker'

urlpatterns = [
    # path('profile/', views.profile_builder, name='profile_builder'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
