# employers/admin.py
from django.contrib import admin
from .models import EmployerProfile

@admin.register(EmployerProfile)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'license_verified')  # ✅ ঠিক
    list_filter = ('license_verified',) 
    actions = ['verify_license']

    def verify_license(self, request, queryset):
        queryset.update(is_verified=True)
    verify_license.short_description = "Verify selected employer licenses"
