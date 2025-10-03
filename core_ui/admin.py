from django.contrib import admin
from .models import FeatureToggle

@admin.register(FeatureToggle)
class FeatureToggleAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'enabled')
    list_editable = ('enabled',)   
    search_fields = ('name', 'key')
