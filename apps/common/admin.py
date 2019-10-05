from django.contrib import admin
from .models import AppInfo, TaskLog


class AppInfoAdmin(admin.ModelAdmin):
    list_display = (
        'app_name',
        'current_version',
        'last_updated',
    )


class TaskLogAdmin(admin.ModelAdmin):
    search_fields = ('task_name', )
    list_filter = ('status', )
    list_display = (
        'task_name',
        'timestamp',
        'status',
        'message'
    )


admin.site.register(AppInfo, AppInfoAdmin)
admin.site.register(TaskLog, TaskLogAdmin)

