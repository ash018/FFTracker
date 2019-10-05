from django.db import models
from django.utils import timezone


class Lead(models.Model):
    name = models.CharField(max_length=255, blank=False)
    phone = models.CharField(max_length=16, blank=False)
    email = models.EmailField()
    company_name = models.CharField(max_length=128, blank=False)
    employee_count = models.CharField(max_length=16, blank=False)
    domain_choice = models.CharField(max_length=255, blank=False)
    designation = models.CharField(max_length=128, blank=False)
    timestamp = models.DateTimeField(default=timezone.now)
