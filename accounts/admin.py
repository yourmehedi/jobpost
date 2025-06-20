from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from employers.models import EmployerProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'user_type', 'telegram_enabled', 'telegram_chat_id', 'is_active', 'is_superuser')
    list_filter = ('user_type', 'telegram_enabled', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'telegram_chat_id')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('User Type Info', {'fields': ('user_type', 'is_verified', 'is_approved', 'has_ai_access')}),
        ('Telegram Settings', {'fields': ('telegram_chat_id', 'telegram_enabled')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'user_type', 'password1', 'password2'),
        }),
    )

    ordering = ('email',)


