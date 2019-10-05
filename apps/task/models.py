import datetime
from django.db import models
from .config import TASK_STATUS_CHOICES, TASK_STATUS_DICT as TSTATE
from apps.user.models import User
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from apps.org.models import Organization
from apps.task.config import default_duration


class Task(models.Model):
    date = models.DateField(default=datetime.date.today, db_index=True)
    org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='task_org',
        null=True
    )
    title = models.CharField(max_length=128, blank=False)
    status = models.PositiveSmallIntegerField(
        default=TSTATE['Unassigned'],
        choices=TASK_STATUS_CHOICES
    )
    start = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField(default=default_duration, db_index=True)
    images = JSONField(null=True, blank=True)

    ts_start = models.DateTimeField(null=True, blank=True)
    ts_finish = models.DateTimeField(null=True, blank=True)
    delayed = models.BooleanField(default=False)

    task_type = models.CharField(max_length=128, blank=False)

    creator = models.ForeignKey(
        User,
        related_name='task_creator',
        on_delete=models.SET_NULL,
        null=True,
        blank=False
    )

    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='task_manager',
        blank=False,
    )
    agent_list = models.ManyToManyField(
        User,
        related_name='user_agents',
        blank=True
    )

    point_start = JSONField(null=True, blank=True)
    point_finish = JSONField(null=True, blank=True)
    point = JSONField(null=True, blank=True)
    address = models.TextField(blank=True)

    image_required = models.BooleanField(default=False)
    attachment_required = models.BooleanField(default=False)
    custom_fields = JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        return self.title


class TaskTemplate(models.Model):
    task_type = models.CharField(max_length=128, blank=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    task_fields = JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        return self.task_type

