from django.contrib import admin
from .models import AISettings

@admin.register(AISettings)
class AISettingsAdmin(admin.ModelAdmin):
    list_display = ("use_openai", "updated_at")
    readonly_fields = ("updated_at",)
