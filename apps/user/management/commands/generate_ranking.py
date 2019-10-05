from django.core.management.base import BaseCommand, CommandError
import logging
from apps.user.models import User
from apps.report.helpers import *
from apps.report.models import AttendanceIndividual as ATI, Ranking
from apps.report.config import ATTENDANCE_STATUS_DICT as ASD
from apps.org.models import Organization

task_logger = logging.getLogger('task_logger')


def create_rk(
        user, org, range_int, date_obj,
        work_hour, min_work_hour, min_task_hour_p
):
    start, end = start_end(date_obj, org.weekend, range_int)

    date_list = []
    cur_date = start
    while cur_date <= end:
        date_list.append(cur_date.date())
        cur_date = cur_date + timezone.timedelta(days=1)

    ati_qs = ATI.objects.filter(
        Q(date__in=date_list) &
        Q(user=user)
    )

    task_qs = Task.objects.filter(
        Q(date__in=date_list) &
        Q(agent_list=user)
    )

    absent = ati_qs.filter(
        Q(status=ASD['Absent'])
    ).count()
    low_work_hour = ati_qs.filter(
        Q(status=ASD['Present']) &
        Q(work_hour__lt=min_work_hour)
    ).count()
    low_task_hour = ati_qs.filter(
        Q(status=ASD['Present']) &
        Q(task_hour_p__lt=min_task_hour_p)
    ).count()
    overtime = ati_qs.filter(Q(work_hour__gt=work_hour)).count()
    late_arrival = ati_qs.filter(Q(late_arrival=True)).count()
    delayed_task = task_qs.filter(Q(delayed=True)).count()

    rk_qs = Ranking.objects.filter(
        Q(user=user) &
        Q(date_range=range_int) &
        Q(date=date_obj.date())
    )

    if rk_qs.exists():
        ranking = rk_qs[0]
    else:
        ranking = Ranking.objects.create(
            org=org, user=user,
            date_range=range_int,
            date=date_obj.date()
        )
    ranking.absence = absent
    ranking.late_arrival = late_arrival
    ranking.low_work_hour = low_work_hour
    ranking.low_task_hour = low_task_hour
    ranking.overtime = overtime
    ranking.delayed_task = delayed_task
    ranking.save()


def generate_ranking_daily(org, date_obj):
    work_hour = get_work_hours(org)
    min_work_hour = work_hour * (org.min_work_hour_p / 100)
    min_task_hour_p = org.min_task_hour_p

    users_qs = User.objects.filter(Q(org=org))
    for user in users_qs:
        # print('Ranking for User: ' + get_username(user))
        create_rk(
            user=user, org=org,
            date_obj=date_obj,
            range_int=RANGE_DICT['this_week'],
            work_hour=work_hour,
            min_work_hour=min_work_hour,
            min_task_hour_p=min_task_hour_p
        )

        create_rk(
            user=user, org=org,
            date_obj=date_obj,
            range_int=RANGE_DICT['last_week'],
            work_hour=work_hour,
            min_work_hour=min_work_hour,
            min_task_hour_p=min_task_hour_p
        )

        create_rk(
            user=user, org=org,
            date_obj=date_obj,
            range_int=RANGE_DICT['this_month'],
            work_hour=work_hour,
            min_work_hour=min_work_hour,
            min_task_hour_p=min_task_hour_p
        )

        create_rk(
            user=user, org=org,
            date_obj=date_obj,
            range_int=RANGE_DICT['last_month'],
            work_hour=work_hour,
            min_work_hour=min_work_hour,
            min_task_hour_p=min_task_hour_p
        )

    return True


def generate_daily_ranking_bg(caller, date_str):
    orgs = Organization.objects.all()

    if not date_str:
        date_obj = timezone.now()
    else:
        date_obj = timezone.datetime.strptime(date_str, '%Y-%m-%d')
        date_obj = utc.localize(date_obj)

    task_logger.info('\n')
    task_logger.info('>>Ranking Date: ' + str(date_obj).split(' ')[0])
    task_logger.info('>>Ranking Creation time: ' + str(timezone.now()).split('.')[0])
    task_logger.info('>>Starting org iteration.....')
    for org in orgs:
        try:
            if org.subscription.current_usage.status == 1:
                generate_ranking_daily(org, date_obj)
        except Exception as e:
            task_logger.debug('>>Org: ' + org.oid)
            task_logger.debug(str(e))


class Command(BaseCommand):
    help = 'Get ranking'

    def add_arguments(self, parser):

        # Optional argument
        parser.add_argument('-d', '--date', type=str, help='Date to create ranking', )

    def handle(self, *args, **options):
        date_str = options.get('prefix', None)
        generate_daily_ranking_bg(self, date_str)

        msg = '>>Successfully Finished ranking generation....'

        task_logger.info(msg)

        self.stdout.write(
            self.style.SUCCESS(
                msg
            )
        )
