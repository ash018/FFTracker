from django.contrib import admin
from .models import Task, TaskTemplate


class TaskAdmin(admin.ModelAdmin):
    search_fields = ('org__oid',)
    list_filter = (
        'status',
        'image_required',
        'attachment_required',
    )

    list_display = (
        'title',
        'id',
        'manager',
        'status',
        'task_type',
        'address',
    )


class TaskTemplateAdmin(admin.ModelAdmin):
    search_fields = ('org__oid',)

    list_display = (
        'task_type',
        'user',
        'org',
    )


admin.site.register(Task, TaskAdmin)
admin.site.register(TaskTemplate, TaskTemplateAdmin)
