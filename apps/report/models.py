import datetime
from django.db import models
from django.utils import timezone
from apps.org.models import Organization
from apps.user.models import User
from apps.task.models import Task

from .config import ATTENDANCE_STATUS_DICT as ASD, \
    ATTENDANCE_STATUS_CHOICES as ASC, RANGE_DICT, RANGE_CHOICES


class TaskCombined(models.Model):
    class Meta:
        verbose_name = 'Task Report'
        verbose_name_plural = 'Task Reports'

    timestamp = models.DateTimeField(default=timezone.now)
    date = models.DateField(default=datetime.date.today, db_index=True)

    delayed = models.ManyToManyField(Task, blank=True, related_name='task_delayed')
    cancelled = models.ManyToManyField(Task, blank=True, related_name='task_cancelled')
    postponed = models.ManyToManyField(Task, blank=True, related_name='task_postponed')
    complete = models.ManyToManyField(Task, blank=True, related_name='task_complete')

    org = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return 'Task_' + str(self.timestamp)


class AttendanceCombined(models.Model):
    class Meta:
        verbose_name = 'Combined Attendance Report'
        verbose_name_plural = 'Combined Attendance Reports'

    timestamp = models.DateTimeField(default=timezone.now)
    date = models.DateField(default=datetime.date.today, db_index=True)

    present = models.ManyToManyField(User, blank=True, related_name='user_present')
    absent = models.ManyToManyField(User, blank=True, related_name='user_absent')
    low_work_hour = models.ManyToManyField(User, blank=True, related_name='user_low_work_hour')
    low_task_hour = models.ManyToManyField(User, blank=True, related_name='user_low_task_hour')
    overtime = models.ManyToManyField(User, blank=True, related_name='user_overtime')
    late_arrival = models.ManyToManyField(User, blank=True, related_name='user_late_arrival')

    org = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.org.oid + '_' + str(self.timestamp.day)


class AttendanceIndividual(models.Model):
    class Meta:
        verbose_name = 'Individual Attendance Report'
        verbose_name_plural = 'Individual Attendance Reports'

    date = models.DateField(default=datetime.date.today, db_index=True)
    user = models.ForeignKey(User, blank=False, null=True, on_delete=models.CASCADE)
    org = models.ForeignKey(Organization, blank=True, null=True, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(
        default=ASD['Absent'],
        choices=ASC
    )

    init_entry_time = models.DateTimeField(default=timezone.now)
    last_entry_time = models.DateTimeField(null=True, blank=True)
    late_arrival = models.BooleanField(default=False)
    exit_time = models.DateTimeField(null=True, blank=True)
    work_hour = models.DurationField(null=True, blank=True)
    task_hour = models.DurationField(null=True, blank=True)
    task_hour_p = models.FloatField(default=0.0, blank=True)
    travel_distance = models.PositiveIntegerField(default=0, blank=True)

    def __str__(self):
        return str(self.user.username)


class Ranking(models.Model):
    class Meta:
        verbose_name = 'Ranking'
        verbose_name_plural = 'Rankings'

    date = models.DateField(default=datetime.date.today, db_index=True)
    user = models.ForeignKey(User, blank=False, null=True, on_delete=models.CASCADE)
    org = models.ForeignKey(Organization, blank=True, null=True, on_delete=models.CASCADE)
    date_range = models.PositiveSmallIntegerField(
        default=RANGE_DICT['this_week'],
        choices=RANGE_CHOICES
    )
    absence = models.PositiveIntegerField(default=0)
    low_task_hour = models.PositiveIntegerField(default=0)
    low_work_hour = models.PositiveIntegerField(default=0)
    overtime = models.PositiveIntegerField(default=0)
    late_arrival = models.PositiveIntegerField(default=0)
    delayed_task = models.PositiveIntegerField(default=0)
    travel_distance = models.PositiveIntegerField(default=0)

