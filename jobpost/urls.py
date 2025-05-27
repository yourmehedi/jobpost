from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('management.urls')),
    path('accounts/', include('accounts.urls')),
    path('social/', include('allauth.urls')),
    path('auth/', include('social_django.urls', namespace='social')), 
    path('chatbot/', include('chatbot.urls')),     
    path('employers/', include('employers.urls')),
    path('jobs/', include('jobs.urls')),
    path('jobseekers/', include('jobseekers.urls')),
    path('ai_engine/', include('ai_engine.urls')),
    path('subscriptions', include('subscriptions.urls')),
    path('resumes/', include('resumes.urls')),
    path('search/', include('search.urls')),
    path('job_recommendation/', include('job_recommendation.urls')),

    
]



urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
