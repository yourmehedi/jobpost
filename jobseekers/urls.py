from django.urls import path
from .views import *

name = 'jobseekers'

urlpatterns = [
    path('profile-builder', profile_builder, name='profile_builder'),
]