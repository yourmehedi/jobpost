from django.contrib import admin
from .models import *


@admin.register(Jobseeker)
class JobseekerAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'contact_number', 'job_type_preference')
    search_fields = ('full_name', 'user__username', 'user__email')
    list_filter = ('job_type_preference',)

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('jobseeker', 'institution', 'degree', 'start_date', 'end_date')

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('jobseeker', 'job_title', 'company_name', 'start_date', 'end_date')

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('jobseeker', 'name', 'proficiency')

@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('jobseeker', 'name', 'company', 'contact_info')

admin.site.register(Skill)
admin.site.register(JobseekerSkill)
admin.site.register(AdditionalInfo)
