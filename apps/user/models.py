import datetime
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager, Permission, PermissionsMixin
from django.db import models
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey

from apps.common.task_templates import DOMAIN_CHOICES
from apps.org.models import Organization
from .config import ROLE_CHOICES, ROLE_DICT


class SimpleUserManager(UserManager):
    def create_user(self, username, **extra_fields):
        # email = self.normalize_email(email)
        user = self.model(username=username, **extra_fields)
        user.is_active = False
        user.is_staff = False
        user.set_password(make_password(password=None))
        user.save(using=self._db)
        print("CREATE USER", extra_fields)
        return user

    def create_superuser(self, username, password, **extra_fields):
        # email = self.normalize_email(email)
        user = self.model(username=username, **extra_fields)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self._db)
        print("CREATE SUPERUSER", extra_fields)
        return user


class User(MPTTModel, AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=32, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=128, null=True, blank=True)
    designation = models.CharField(max_length=128, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)

    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    role = models.PositiveSmallIntegerField(
        default=ROLE_DICT['Employee'],
        choices=ROLE_CHOICES, blank=True
    )

    is_present = models.BooleanField(default=False)
    is_awol = models.BooleanField(default=False)
    is_working = models.BooleanField(default=False)
    ping_count = models.PositiveIntegerField(default=0)

    parent = TreeForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='children'
    )

    date_joined = models.DateTimeField(default=timezone.now)
    image = models.URLField(null=True, blank=True)
    domain = models.PositiveSmallIntegerField(default=0, choices=DOMAIN_CHOICES)
    org = models.ForeignKey(
        Organization, null=True, blank=True,
        on_delete=models.CASCADE
    )
    fb_token = models.TextField(null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = SimpleUserManager()

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name

    def __str__(self):
        return self.username


class DataUsage(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    total_megabytes = models.FloatField(default=0.0)
    device_megabytes = models.FloatField(default=0.0)
    instant_megabytes = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(default=timezone.now)
    mac = models.CharField(max_length=64, blank=True, default='')
    date = models.DateField(default=datetime.date.today, db_index=True)
