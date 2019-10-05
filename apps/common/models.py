from django.db import models
from django.utils import timezone


class AppInfo(models.Model):
    APP_CHOICES = (
        ('manager', 'manager'),
        ('agent', 'agent')
    )
    app_name = models.CharField(
        max_length=128,
        default='manager',
        choices=APP_CHOICES
    )
    current_version = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.app_name


class TaskLog(models.Model):
    STATUS_CHOICES = (
        (0, 'started'),
        (1, 'finished'),
        (2, 'failed')
    )
    task_name = models.CharField(max_length=64, blank=True, default='')
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    message = models.TextField(blank=True, default='')
    status = models.PositiveIntegerField(default=0, choices=STATUS_CHOICES)

    def __str__(self):
        return self.task_name
