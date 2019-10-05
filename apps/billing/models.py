from django.db import models
# from django.db.models import F
from django.utils import timezone
from apps.user.models import User
from django.contrib.postgres.fields import JSONField
from apps.org.models import Organization
from apps.billing.config import *
from apps.common.helpers import inc_field


def default_cycle():
    return timezone.now() + timezone.timedelta(days=BILL_CYCLE)


def extend_cycle(cur_exp):
    return cur_exp + timezone.timedelta(days=BILL_CYCLE)


class Usage(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    init_date = models.DateTimeField(default=timezone.now)
    exp_date = models.DateTimeField(default=default_cycle)
    consumed_tasks = models.PositiveIntegerField(default=0)
    bill_subscription = models.FloatField(default=0.0)
    bill_new_agent = models.FloatField(default=0.0)
    bill_extra_task = models.FloatField(default=0.0)
    package = models.PositiveSmallIntegerField(
        choices=PACKAGE_CHOICES,
        default=PACKAGE_IDS['None']
    )
    discount = models.FloatField(default=0.0)
    status = models.PositiveSmallIntegerField(choices=USAGE_CHOICE, default=1)

    def __str__(self):
        if self.org:
            return self.org.oid + '_' + str(self.exp_date)
        return '_' + str(self.exp_date)


class Subscription(models.Model):
    org = models.OneToOneField(Organization, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(default=timezone.now)
    agent_limit = models.PositiveIntegerField(default=FREE_AGENT)
    added_agents = models.PositiveIntegerField(default=0)
    task_limit = models.PositiveIntegerField(default=FREE_TASK)
    currency = models.PositiveSmallIntegerField(choices=CURRENCY_CHOICE, default=1)
    package = models.PositiveSmallIntegerField(
        choices=PACKAGE_CHOICES,
        default=PACKAGE_IDS['None']
    )
    _is_premium = models.BooleanField(default=False)
    _is_trial = models.BooleanField(default=False)
    _next_due = models.FloatField(default=0.0)
    renew_needed = models.BooleanField(default=False)
    current_usage = models.ForeignKey(Usage, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        if self.org:
            return self.org.oid
        return 'None'

    def get_task_price(self, tasks):
        return EXTRA_TASK_PRICE * tasks

    def new_subscription_bill(self, promo_code=False):
        package_info = PACKAGE_INFO[self.package]
        if self.added_agents > 0:
            if self._is_premium:
                bill = (package_info['price'] + PREMIUM_STORAGE) * self.added_agents
            else:
                bill = package_info['price'] * self.added_agents
        else:
            if self._is_premium:
                bill = package_info['price'] + PREMIUM_STORAGE
            else:
                bill = package_info['price']
        if promo_code:
            # TODO: Promo CODE
            pass
        return float(bill)

    def new_task_bill(self, tasks, promo_code=False):
        bill = self.get_task_price(tasks)
        if promo_code:
            # TODO: Promo CODE
            pass
        return float(bill)

    def new_agent_bill(self, agents, promo_code=False):
        package_info = PACKAGE_INFO[self.package]
        if self._is_premium:
            bill = (package_info['price'] + PREMIUM_STORAGE) * agents
        else:
            bill = package_info['price'] * agents
        if promo_code:
            # TODO: Promo CODE
            pass
        return float(bill)

    def renew_subscription(self, bill=0.0):
        task_packs = [PACKAGE_IDS['Full Suite'], PACKAGE_IDS['Task Management']]
        if self.added_agents > 0:
            self.agent_limit = self.added_agents
            if self.package in task_packs:
                self.task_limit = MONTHLY_AVG_TASK * self.added_agents
            else:
                self.task_limit = 0
        else:
            self.added_agents = 0
            self.agent_limit = 1
            if self.package in task_packs:
                self.task_limit = MONTHLY_AVG_TASK
            else:
                self.task_limit = 0

        self.current_usage.status = USAGE_DICT['expired']
        # expiring for early renew
        self.current_usage.save()

        # TODO: Include discount
        new_usage = Usage(
            bill_subscription=bill,
            org=self.org,
            package=self.package,
        )
        new_usage.save()

        self._is_trial = False
        self.current_usage = new_usage
        self.renew_needed = False
        self.save()

    def add_new_agents(self, agents, bill=0.0):
        inc_field(self, 'agent_limit', agents)
        if self.package == PACKAGE_IDS['Full Suite']:
            inc_field(self, 'task_limit', MONTHLY_AVG_TASK * agents)
        inc_field(self.current_usage, 'bill_new_agent', bill)

    def add_extra_tasks(self, tasks, bill=0.0):
        inc_field(self, 'task_limit', tasks)
        inc_field(self.current_usage, 'bill_extra_task', bill)


class Payment(models.Model):
    gateway = models.PositiveSmallIntegerField(choices=GATEWAY_CHOICES, default=1, blank=False)
    vendor_uid = models.CharField(max_length=255, blank=False, unique=True)
    payment_uid = models.CharField(max_length=255, blank=False, null=True)
    state = models.PositiveSmallIntegerField(
        default=PAYMENT_STATUS_DICT['Initiated'],
        choices=PAYMENT_STATUS_CHOICES
    )
    amount = models.FloatField(default=0.0, blank=False)
    package = models.PositiveSmallIntegerField(
        choices=PACKAGE_CHOICES,
        default=PACKAGE_IDS['None']
    )
    bill_type = models.PositiveSmallIntegerField(
        choices=BILL_CHOICES,
        default=BILL_TYPES['New subscription'],
        blank=False
    )
    extra_tasks = models.PositiveIntegerField(default=0)
    new_agents = models.PositiveIntegerField(default=0)

    details = JSONField(null=True, blank=True)
    currency = models.PositiveSmallIntegerField(choices=CURRENCY_CHOICE, default=1)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
