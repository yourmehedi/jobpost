# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'user_type', 'is_verified', 'is_active', 'is_superuser')
    list_filter = ('user_type', 'is_verified', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('User Type Info', {'fields': ('user_type', 'is_verified', 'is_approved')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'user_type', 'password1', 'password2'),
        }),
    )
    ordering = ('email',)


class EmployerAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'employer_type', 'tin', 'is_approved')
    list_filter = ('employer_type', 'is_approved')
    search_fields = ('company_name', 'user__username', 'user__email')
