from django.db import models
from django.utils import timezone
from apps.user.models import User
from django.contrib.postgres.fields import JSONField
from apps.task.models import Task
from apps.assignment.models import Assignment
from .config import NOTIFICATION_CHOICES, NOTIFICATION_DICT as NTD


class Notification(models.Model):
    title = models.CharField(max_length=128, blank=False)
    text = models.CharField(max_length=200, blank=True)
    type = models.PositiveSmallIntegerField(
        default=NTD['Alert'],
        choices=NOTIFICATION_CHOICES
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    task = models.ForeignKey(Task, null=True, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, null=True, on_delete=models.CASCADE)
    agent = models.ForeignKey(
        User,
        related_name='user_agent',
        on_delete=models.CASCADE,
        null=True
    )
    recipients = models.ManyToManyField(
        User,
        related_name='user_recipients',
        blank=True
    )
    recipient = models.ForeignKey(
        User,
        related_name='user_recipient',
        on_delete=models.CASCADE,
        blank=True, null=True
    )

    point = JSONField(null=True, blank=True)
    images = JSONField(null=True, blank=True)
    address = models.TextField(blank=True)
    checked = models.BooleanField(default=False)

    def __str__(self):
        return self.title
