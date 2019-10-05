from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import DataUsage
User = get_user_model()


class UserAdmin(BaseUserAdmin):

    list_display = (
        'username',
        'phone',
        'email',
        'full_name',
        'date_joined',
        'is_working',
        'ping_count',
        'is_active', 'is_staff',
        'role',
    )

    list_filter = ('is_staff', 'is_active', 'ping_count', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': (
            'username',
            'full_name',
            'phone',
            'fb_token',
            'is_working',
            'is_present',
            'is_awol',
            'org',
            'ping_count',
        )}),
        ('Permissions', {
            'fields': (
                'is_staff', 'is_active', 'role'
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}
        ),
    )
    search_fields = ('username', 'org__org_name')
    ordering = ('username',)
    filter_horizontal = ()


class DataUsageAdmin(admin.ModelAdmin):
    list_filter = (
        'agent__org',
    )

    search_fields = (
        'agent__username',
    )

    list_display = (
        'agent',
        'total_megabytes',
        'device_megabytes',
        'instant_megabytes',
        'timestamp',
    )


admin.site.register(User, UserAdmin)
admin.site.register(DataUsage, DataUsageAdmin)
