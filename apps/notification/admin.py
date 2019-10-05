from django.contrib import admin
from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_filter = (
        'type',
        'timestamp',
    )

    list_display = (
        'title',
        'type',
        'timestamp',
        'task',
        'agent',
        'get_receivers',
    )

    def get_receivers(self, obj):
        return ", ".join([p.full_name for p in obj.recipients.all()])

    get_receivers.short_description = 'Recipients'


admin.site.register(Notification, NotificationAdmin)
