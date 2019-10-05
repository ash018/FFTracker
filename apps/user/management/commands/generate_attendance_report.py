import logging
import pytz
from django.core.management.base import BaseCommand, CommandError

from apps.user.models import User
from apps.user.config import ROLE_DICT
from apps.report.helpers import *
from apps.report.models import AttendanceIndividual as ATI, AttendanceCombined as ATC
from apps.report.config import ATTENDANCE_STATUS_DICT as ASD
from apps.org.models import Organization

utc = pytz.UTC

task_logger = logging.getLogger('task_logger')


def generate_atc_daily(org, date_obj):

    atc_filter = Q(
        date=date_obj.date()
    ) & Q(
        org=org
    )

    present = []
    absent = []
    low_work_hour_list = []
    low_task_hour_list = []
    late_arrival_list = []
    # overtime_list = []

    qfilter_users = Q(org=org) & Q(is_active=True)
    qfilter_users &= Q(role__in=[ROLE_DICT['Manager'], ROLE_DICT['Employee']])
    users = User.objects.filter(qfilter_users)

    min_work_hour = get_work_hours(org) * (org.min_work_hour_p/100)

    for user in users:
        ati_user = Q(date=date_obj.date()) & Q(user=user)
        is_present = Q(status=ASD['Present'])
        is_away = Q(status=ASD['Absent']) | Q(status=ASD['Weekend'])

        if ATI.objects.filter(ati_user & is_present).exists():
            present.append(user)
            if ATI.objects.filter(ati_user & is_away).exists():
                ati_abs_qs = ATI.objects.filter(ati_user & is_away)
                logging.debug('Deleting absent/weekend entry..')
                for ati_abs in ati_abs_qs:
                    ati_abs.delete()

            ati = ATI.objects.filter(ati_user)[0]
            if ati.late_arrival:
                late_arrival_list.append(user)
            # check for null work_hour
            if not ati.work_hour or ati.work_hour < min_work_hour:
                low_work_hour_list.append(user)
            if ati.task_hour_p < org.min_task_hour_p and user.role == ROLE_DICT['Employee']:
                # only including field agents
                low_task_hour_list.append(user)
        else:
            if date_obj.weekday() not in user.org.weekend:
                absent.append(user)

            if ATI.objects.filter(ati_user & is_away).exists():
                pass
            else:
                if date_obj.weekday() in user.org.weekend:
                    ati = ATI.objects.create(
                        user=user, org=user.org,
                        date=date_obj.date(),
                        status=ASD['Weekend'],
                    )
                else:
                    ati = ATI.objects.create(
                        user=user, org=user.org,
                        date=date_obj.date(),
                        status=ASD['Absent'],
                    )

    if ATC.objects.filter(atc_filter).exists():
        atc = ATC.objects.filter(atc_filter)[0]
    else:
        atc = ATC.objects.create(
            org=org,
            date=date_obj.date(),
        )

    atc.absent.clear()
    atc.absent.add(*absent)

    atc.present.clear()
    atc.present.add(*present)

    atc.low_work_hour.clear()
    atc.low_work_hour.add(*low_work_hour_list)

    atc.low_task_hour.clear()
    atc.low_task_hour.add(*low_task_hour_list)

    # atc.overtime.clear()
    # atc.overtime.add(*overtime_list)

    atc.late_arrival.clear()
    atc.late_arrival.add(*late_arrival_list)

    atc.save()

    return True


def generate_daily_reports_bg(caller, date_str):
    orgs = Organization.objects.select_related(
        'subscription',
        'subscription__current_usage'
    ).all()

    if not date_str:
        date_obj = timezone.now()
    else:
        date_obj = timezone.datetime.strptime(date_str, '%Y-%m-%d')
        date_obj = utc.localize(date_obj)

    task_logger.info('\n')
    task_logger.info('>>Attendance Date: ' + str(date_obj).split(' ')[0])
    task_logger.info('>>Attendance Creation time: ' + str(timezone.now()).split('.')[0])
    task_logger.info('>>Starting org iteration.....')
    for org in orgs:
        try:
            if org.subscription.current_usage.status == 1:
                generate_atc_daily(org, date_obj)
        except Exception as e:
            task_logger.debug('>>Org: ' + org.oid)
            task_logger.debug(str(e))


class Command(BaseCommand):
    help = 'Get attendance report'

    def add_arguments(self, parser):

        # Optional argument
        parser.add_argument('-d', '--date', type=str, help='Date to create attendance report', )

    def handle(self, *args, **options):
        date_str = options.get('date', None)
        generate_daily_reports_bg(self, date_str)
        msg = '>>Successfully Finished attendance report generation....'

        task_logger.info(msg)

        self.stdout.write(
            self.style.SUCCESS(
                msg
            )
        )
