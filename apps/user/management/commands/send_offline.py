import pytz
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import logging
from django.db.models import Q

from apps.user.models import User
from apps.user.helpers import ROLE_DICT
from apps.notification.transmitters import force_offline_notification
from apps.location.config import EVENT_DICT
from apps.location.helpers import exec_offline_event
from apps.location.models import Location
from apps.common.models import TaskLog

task_logger = logging.getLogger('task_logger')
utc = pytz.UTC


def send_offline_bg(caller, task_log):
    qcommon_resource = Q(
        role__in=[ROLE_DICT['Manager'], ROLE_DICT['Employee']]
    ) & Q(
        is_present=True
    )
    online_resource_qs = User.objects.filter(
        qcommon_resource
    ).select_related(
        'org', 'userstate'
    )
    # task_logger.info('Starting send offline loop......')
    this_time = timezone.datetime.now()
    # task_logger.info('Send offline timestamp: ' + str(this_time))
    today = this_time.date()
    for rcs in online_resource_qs:
        day_end = rcs.org.day_end
        end_time = timezone.datetime.combine(today, day_end)
        # print('office end: ' + str(end_time))
        # print('Current: ' + str(this_time))
        if this_time > end_time:
            try:
                location_qs = Location.objects.filter(
                    Q(agent_id=rcs.id)
                ).order_by('-timestamp')
                User.objects.filter(
                    id=rcs.id
                ).update(is_awol=False, is_present=False)
                if location_qs.exists():
                    exec_offline_event(user=rcs, exit_timestamp=utc.localize(this_time))
                    location = location_qs[0]
                    location.event = EVENT_DICT['To Offline']
                    location.id = None
                    location.timestamp = utc.localize(this_time)
                    location.save()
                    # print('Sending force offline notification to: ' + rcs.username)
                    # task_logger.info('>>Sending force offline notification to: ' + rcs.username)
                    task_msg = '>>Sending force offline notification to: ' + rcs.username + '\n'
                    task_log.message = task_log.message + task_msg
                    force_offline_notification(rcs)
            except Exception as e:
                task_msg = '>>User: '+rcs.username + ', exception:  ' + str(e) + '\n'
                task_log.message = task_log.message + task_msg
    task_msg = '>>Successfully Sent agents offline....\n'
    task_log.message = task_log.message + task_msg
    task_log.status = 1
    task_log.save()


class Command(BaseCommand):
    help = 'Send agents offline with notifications'

    def handle(self, *args, **options):
        task_log = TaskLog(
            task_name='send_offline',
            message='>>Starting send offline loop\n'
        )
        try:
            send_offline_bg(self, task_log)
            msg = 'Successfully Sent agents offline....'
            # task_logger.info(msg)
            self.stdout.write(self.style.SUCCESS(msg))
        except Exception as e:

            task_msg = 'Exception:  ' + str(e) + '\n'
            task_log.message = task_log.message + task_msg
            task_log.status = 2
            task_log.save()

