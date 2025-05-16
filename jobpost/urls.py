from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('management.urls')),
    path('accounts/', include('accounts.urls')),
    path('social/', include('allauth.urls')),      
    path('employers/', include('employers.urls')),
    path('jobs/', include('jobs.urls')),
    path('jobseekers/', include('jobseekers.urls')),
    path('ai_engine/', include('ai_engine.urls')),
    path('subscriptions', include('subscriptions.urls')),
]



urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
