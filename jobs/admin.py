from django.contrib import admin
from .models import *

admin.site.register(Job)
admin.site.register(Company)
admin.site.register(SavedJob)

@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    actions = ['approve_job']

    def approve_job(self, request, queryset):
        queryset.update(is_approved=True)
    approve_job.short_description = "Approve selected job posts"


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'job', 'applied_at')
    search_fields = ('name', 'email', 'job__title')