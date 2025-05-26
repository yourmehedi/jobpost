from django.contrib import admin
from .models import RestrictedWord

@admin.register(RestrictedWord)
class RestrictedWordAdmin(admin.ModelAdmin):
    list_display = ('word',)
    search_fields = ('word',)
