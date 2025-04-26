
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('management.urls')),
    path('employers/', include('employers.urls')),
    path('accounts/', include('accounts.urls')),
    path('jobs/', include('jobs.urls')),
]
