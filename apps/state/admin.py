from django.contrib import admin
from .models import UserState


class UserStateAdmin(admin.ModelAdmin):

    list_filter = (
        'user__org',
    )
    raw_id_fields = ('active_task', 'last_location',)

    list_display = (
        'user',
        'last_location',
        'active_task',
        'current_device',
    )

    search_fields = ('user__username',)
    ordering = ('user__username',)


admin.site.register(UserState, UserStateAdmin)
