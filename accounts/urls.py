from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import login_view
from .forms import CustomLoginForm

app_name = 'accounts'

urlpatterns = [
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('profile/', views.user_profile, name='profile'),
    path('jobseekres-registretion-form/', views.jobseeker_register, name='jobseeker_register'),
    path('employer-registretion-form/', views.employer_register, name='employer_register'),
    
    path('logout/', views.logout_view, name='logout'),
    path('login/', login_view, name='login'),

    path("google/login/", views.google_login, name="google_login"),
    path("google/callback/", views.google_callback, name="google_callback"),

    path("facebook/login/", views.facebook_login, name="facebook_login"),
    path("facebook/callback/", views.facebook_callback, name="facebook_callback"),
]
