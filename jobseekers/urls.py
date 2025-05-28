from django.urls import path
from . import views

app_name = 'jobseeker'

urlpatterns = [
    path('profile/', views.profile_builder, name='profile_builder'),
    path('profile/view/', views.profile_view, name='profile_view'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
