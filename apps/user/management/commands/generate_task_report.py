import pytz
import datetime
from django.core.management.base import BaseCommand, CommandError

from apps.report.helpers import *
from apps.report.models import TaskCombined as TC
from apps.task.models import Task
from apps.task.config import TASK_STATUS_DICT as TSD

from apps.org.models import Organization

utc = pytz.UTC


def generate_task_combined_daily(org, date_str=None):
    if not date_str:
        date_obj = timezone.now()
    else:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        date_obj = utc.localize(date_obj)

    deadline_filter = Q(date=date_obj.date()) & Q(org=org)

    tc_filter = Q(date=date_obj.date()) & Q(org=org)
    complete = []
    cancelled = []
    postponed = []
    delayed = []

    users = Task.objects.filter(deadline_filter)

    for task in users:
        if task.status == TSD['Complete']:
            complete.append(task)
        if task.status == TSD['Cancelled']:
            cancelled.append(task)
        if task.delayed:
            delayed.append(task)
        if task.status == TSD['Postponed']:
            postponed.append(task)

    if TC.objects.filter(tc_filter).exists():
        tc = TC.objects.filter(tc_filter)[0]
    else:
        tc = TC.objects.create(
            org=org,
            timestamp=date_obj,
        )

    tc.complete.clear()
    tc.complete.add(*complete)

    tc.cancelled.clear()
    tc.cancelled.add(*cancelled)

    tc.delayed.clear()
    tc.delayed.add(*delayed)

    tc.postponed.clear()
    tc.postponed.add(*postponed)

    tc.save()

    return True


def generate_daily_reports_bg(caller, date_str):
    orgs = Organization.objects.select_related(
        'subscription',
        'subscription__current_usage'
    ).all()
    caller.stdout.write('Starting org iteration.....')
    for org in orgs:
        try:
            if org.subscription.current_usage.status == 1:
                generate_task_combined_daily(org, date_str)
        except Exception as e:
            print('Org: ' + org.oid)
            print(str(e))


class Command(BaseCommand):
    help = 'Get task report'

    def add_arguments(self, parser):

        # Optional argument
        parser.add_argument('-d', '--date', type=str, help='Date to create task report', )

    def handle(self, *args, **options):
        date_str = options.get('prefix', None)
        generate_daily_reports_bg(self, date_str)

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully Finished task report generation....'
            )
        )
