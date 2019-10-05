import datetime
from django.db import models
from django.utils import timezone
from apps.org.models import Organization
from apps.user.models import User
from apps.task.models import Task
from django.contrib.postgres.fields import JSONField
from .config import EVENT_CHOICES, EVENT_DICT


class Location(models.Model):
    org = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    date = models.DateField(default=datetime.date.today, db_index=True)
    event = models.PositiveSmallIntegerField(
        default=EVENT_DICT['No Task'],
        choices=EVENT_CHOICES
    )
    point = JSONField(null=True)
    address = models.CharField(max_length=512, blank=True, default='')
    agent = models.ForeignKey(
        User, null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    mac = models.CharField(max_length=64, blank=True, default='')
    on_task = models.ForeignKey(
        Task, null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='on_task'
    )

    def __str__(self):
        for key, value in EVENT_DICT.items():
            if value == self.event:
                return str(key)
        return 'No Task'


class ClientLocation(models.Model):
    org = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)
    point = JSONField(null=True)
    name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=512, blank=True)

    def __str__(self):
        return self.name

