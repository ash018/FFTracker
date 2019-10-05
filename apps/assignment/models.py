from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from apps.org.models import Organization
from apps.user.models import User
from .config import ASSIGNMENT_STATUS_DICT as ASD, ASSIGNMENT_STATUS_CHOICES as ASC, default_deadline


class Assignment(models.Model):
    org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True
    )
    title = models.CharField(max_length=128, blank=False)
    description = models.CharField(max_length=512, default='', blank=True)
    status = models.PositiveSmallIntegerField(
        default=ASD['Remaining'],
        choices=ASC,
        blank=True,
    )
    created = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField(default=default_deadline, db_index=True)
    progress = models.PositiveIntegerField(default=0)

    creator = models.ForeignKey(
        User, related_name='assignment_creator',
        on_delete=models.SET_NULL,
        null=True, blank=False
    )
    manager = models.ForeignKey(
        User, related_name='assignment_manager',
        on_delete=models.SET_NULL,
        null=True, blank=False
    )

    assignee = models.ForeignKey(
        User, related_name='assignment_assignee',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    assignee_list = models.ManyToManyField(
        User,
        related_name='user_assignees',
        blank=True
    )

    custom_fields = JSONField(default=dict, null=True, blank=True)
    checklist = JSONField(default=list, null=True, blank=True)


class Comment(models.Model):
    text = models.TextField(blank=True)
    attachments = JSONField(null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        null=True,
        blank=False
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        null=True,
        blank=False
    )
