from django.urls import path
from . import views

app_name = 'jobseeker'

urlpatterns = [
    path('profile/profile-builder', views.profile_builder, name='profile_builder'),
    path('profile/view/', views.profile_view, name='profile_view'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('settings/', views.account_settings, name='account_settings'),
]
