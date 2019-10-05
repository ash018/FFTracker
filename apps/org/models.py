import datetime
from django.db import models
from django.utils import timezone
from apps.org.config import STATUS_CHOICES, WEEKDAY_CHOICES, default_weekend
from django.contrib.postgres.fields import ArrayField


class Reseller(models.Model):
    name = models.CharField(max_length=128, blank=False)
    info = models.CharField(max_length=255, blank=True)
    panel_link = models.URLField(null=True, blank=True)


class Organization(models.Model):
    oid = models.CharField(max_length=32, unique=True)
    org_name = models.CharField(max_length=128, blank=True, null=True)
    status = models.PositiveSmallIntegerField(default=1, choices=STATUS_CHOICES)
    date_created = models.DateTimeField(default=timezone.now)
    address = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    logo = models.URLField(null=True, blank=True)

    day_start = models.TimeField(default=datetime.time(9, 0, 0), null=True)
    day_end = models.TimeField(default=datetime.time(17, 0, 0), null=True)
    location_interval = models.PositiveIntegerField(default=120, null=True)
    org_set = models.BooleanField(default=False)
    min_work_hour_p = models.PositiveIntegerField(default=90, blank=True)
    min_task_hour_p = models.PositiveIntegerField(default=50, blank=True)
    tracking_enabled = models.BooleanField(default=True)

    weekend = ArrayField(
        models.PositiveSmallIntegerField(
            choices=WEEKDAY_CHOICES
        ),
        default=default_weekend,
        blank=True
    )

    has_reseller = models.BooleanField(default=False)
    reseller_name = models.CharField(max_length=64, blank=True)
    reseller_info = models.CharField(max_length=255, blank=True)
    reseller_panel_link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.oid

