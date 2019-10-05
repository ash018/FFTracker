from django.contrib import admin
from .models import Assignment


class AssignmentAdmin(admin.ModelAdmin):
    search_fields = ('org__oid', )

    list_filter = (
        'status',
    )

    list_display = (
        'title',
        'status',
        'manager',
        'assignee',
        'deadline',
    )


admin.site.register(Assignment, AssignmentAdmin)
