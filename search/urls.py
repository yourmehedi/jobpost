from django.urls import path
from .views import tag_search

app_name = 'search'

urlpatterns = [
    path('tags/', tag_search, name='tag_search'),
]
