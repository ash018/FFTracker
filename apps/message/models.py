from django.db import models
from django.utils import timezone
from apps.user.models import User
from django.contrib.postgres.fields import JSONField
from apps.org.models import Organization
from .config import MSG_CHOICES, MSG_DICT as MSGD


class Thread(models.Model):
    name = models.CharField(max_length=128, blank=False)
    org = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(default=MSGD['Private'], choices=MSG_CHOICES)
    members = models.ManyToManyField(
        User, related_name='user_msg_group', blank=True
    )
    admin = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    creation_time = models.DateTimeField(default=timezone.now)
    last_message_time = models.DateTimeField(default=timezone.now, db_index=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    text = models.TextField(blank=True)
    attachments = JSONField(null=True)
    type = models.PositiveSmallIntegerField(default=MSGD['Private'], choices=MSG_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    sender = models.ForeignKey(User, null=True, on_delete=models.CASCADE,
                               related_name='user_sender')
    group = models.ForeignKey(Thread, null=True, on_delete=models.CASCADE)
