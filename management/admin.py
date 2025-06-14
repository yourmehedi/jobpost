from django.contrib import admin
from .models import *



@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'employer_type', 'approval_status', 'is_active', 'created_on')
    list_filter = ('employer_type', 'approval_status', 'is_active')
    search_fields = ('company_name', 'user__username', 'user__email')
    actions = ['approve_selected', 'reject_selected']

    def approve_selected(self, request, queryset):
        queryset.update(approval_status='approved')
    approve_selected.short_description = "Approve selected employers"

    def reject_selected(self, request, queryset):
        queryset.update(approval_status='rejected')
    reject_selected.short_description = "Reject selected employers"
