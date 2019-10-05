from django.db import models
from django.utils import timezone

from apps.org.models import Organization
from apps.user.models import User
from .config import SUPPORT_STATUS_CHOICES as SSC, SUPPORT_STATUS_DICT as SSD


class CustomerSupport(models.Model):
    org = models.ForeignKey(Organization, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=False)
    date_created = models.DateTimeField(default=timezone.now)
    status = models.PositiveSmallIntegerField(default=SSD['Pending'], choices=SSC)

    def __str__(self):
        return self.subject

