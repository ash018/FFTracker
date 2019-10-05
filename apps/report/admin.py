from django.contrib import admin
from .models import AttendanceCombined, TaskCombined, AttendanceIndividual


class AttendanceCombinedAdmin(admin.ModelAdmin):
    list_filter = (
        'org',
    )

    list_display = (
        'org',
        'date',
        'get_present',
        'get_absent',
        'get_low_work_hour',
        'get_low_task_hour',
        'get_overtime',
        'get_late_arrival'
    )

    def get_present(self, obj):
        return ", ".join([p.full_name for p in obj.present.all()])

    def get_absent(self, obj):
        return ", ".join([p.full_name for p in obj.absent.all()])

    def get_low_work_hour(self, obj):
        return ", ".join([p.full_name for p in obj.low_work_hour.all()])

    def get_low_task_hour(self, obj):
        return ", ".join([p.full_name for p in obj.low_task_hour.all()])

    def get_overtime(self, obj):
        return ", ".join([p.full_name for p in obj.overtime.all()])

    def get_late_arrival(self, obj):
        return ", ".join([p.full_name for p in obj.late_arrival.all()])

    get_present.short_description = 'Present'
    get_absent.short_description = 'Absent'
    get_low_work_hour.short_description = 'Low work hour'
    get_low_task_hour.short_description = 'Low task hour'
    get_overtime.short_description = 'Overtime'
    get_late_arrival.short_description = 'Late arrival'


class TaskCombinedAdmin(admin.ModelAdmin):
    list_filter = (
        'org',
    )

    list_display = (
        'org',
        'date',
        'get_complete',
        'get_cancelled',
        'get_delayed',
        'get_postponed',
    )

    def get_complete(self, obj):
        return ", ".join([p.title for p in obj.complete.all()])

    def get_cancelled(self, obj):
        return ", ".join([p.title for p in obj.cancelled.all()])

    def get_delayed(self, obj):
        return ", ".join([p.title for p in obj.delayed.all()])

    def get_postponed(self, obj):
        return ", ".join([p.title for p in obj.postponed.all()])

    get_complete.short_description = "Complete"
    get_cancelled.short_description = "Cancelled"
    get_delayed.short_description = "Delayed"
    get_postponed.short_description = "Postponed"


class AttendanceIndividualAdmin(admin.ModelAdmin):
    list_filter = (
        'org', 'status', 'init_entry_time'
    )

    list_display = (
        'employee',
        'org',
        'status',
        'init_entry_time',
        'last_entry_time',
        'exit_time',
        'work_hour',
        'task_hour_p',
    )

    def employee(self, obj):
        return obj.user.full_name


admin.site.register(AttendanceCombined, AttendanceCombinedAdmin)
admin.site.register(TaskCombined, TaskCombinedAdmin)
admin.site.register(AttendanceIndividual, AttendanceIndividualAdmin)
