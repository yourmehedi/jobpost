from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from employers.models import EmployerProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'user_type', 'is_verified', 'is_active', 'is_superuser')
    list_filter = ('user_type', 'is_verified', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('User Type Info', {'fields': ('user_type', 'is_verified', 'is_approved', 'has_ai_access')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'user_type', 'password1', 'password2'),
        }),
    )

    ordering = ('email',)


