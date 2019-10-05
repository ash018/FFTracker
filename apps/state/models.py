from django.db import models
from django.utils import timezone
import datetime
from apps.org.models import Organization
from apps.user.models import User
from apps.task.models import Task
from apps.location.models import Location


class DeviceHistory(models.Model):
    user = models.ForeignKey(
        User, blank=False,
        on_delete=models.CASCADE
    )
    mac = models.CharField(max_length=64, null=True, blank=True, default='')
    model_no = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(default=datetime.date.today)
    timestamp = models.DateField(default=timezone.datetime.now)

    def __str__(self):
        return self.model_no + '_' + self.user.username


class UserState(models.Model):
    user = models.OneToOneField(
        User, blank=False,
        on_delete=models.CASCADE
    )

    is_present = models.BooleanField(default=False)
    is_awol = models.BooleanField(default=False)
    is_working = models.BooleanField(default=False)
    fb_token = models.TextField(null=True, blank=True)

    active_task = models.ForeignKey(
        Task, blank=True, null=True,
        on_delete=models.SET_NULL
    )
    last_location = models.ForeignKey(
        Location, blank=True, null=True,
        on_delete=models.SET_NULL
    )
    current_device = models.ForeignKey(
        DeviceHistory, null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return 'state_' + self.user.username
