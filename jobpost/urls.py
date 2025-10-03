from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf import settings

urlpatterns = [
    path('admin', admin.site.urls),
    path('', include('management.urls')),
    path('accounts/', include('accounts.urls')),
    
    path('chatbot/', include('chatbot.urls')),     
    path('employers/', include('employers.urls')),
    path('jobs/', include('jobs.urls')),
    path('jobseekers/', include('jobseekers.urls')),
    path('ai/', include('ai_engine.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('resumes/', include('resumes.urls')),
    path('search/', include('search.urls')),
    path('job_recommendation/', include('job_recommendation.urls')),
    path('communications/', include('communications.urls')),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("auth/", include("social_django.urls", namespace="social")),


]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

