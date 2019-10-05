from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import logging
from django.db.models import Q
from django.db.models import F

from apps.user.models import User
from apps.user.helpers import ROLE_DICT
from apps.notification.transmitters import unreachable_notification, ping_device
from apps.notification.config import NOTIFICATION_DICT as NTD
from apps.location.models import Location
from apps.location.config import EVENT_DICT
from apps.billing.config import PACKAGE_IDS

task_logger = logging.getLogger('task_logger')
MAX_PING = 3


def get_unreachables_bg(caller):
    qcommon_resource = Q(
        role__in=[ROLE_DICT['Manager'], ROLE_DICT['Employee']]
    ) & Q(
        is_awol=False
    ) & Q(
        is_present=True
    )
    online_resource = User.objects.filter(
        qcommon_resource
    ).select_related('org')
    task_logger.info('Starting unreachables loop......')
    this_time = timezone.datetime.now()
    task_logger.info('Unreachables timestamp: ' + str(this_time))
    for resource in online_resource:
        tracking_packs = [PACKAGE_IDS['Full Suite'], PACKAGE_IDS['Tracking']]
        package = resource.org.subscription.package
        if package not in tracking_packs:
            continue
        loc_qs = Location.objects.filter(agent=resource)
        resource_qs = User.objects.filter(id=resource.id)
        loc_interval = resource.org.location_interval
        ping_lim = timezone.timedelta(seconds=loc_interval * 3)
        if loc_qs.exists():
            location = loc_qs.order_by('-timestamp')[0]
            time_diff = timezone.now() - location.timestamp

            if time_diff > ping_lim:
                if resource.ping_count >= MAX_PING:
                    task_logger.info(resource.username + ' went OOC!')
                    # resource.is_awol = True
                    # resource.save()
                    resource_qs.update(is_awol=True)
                    location.event = EVENT_DICT['To OOC']
                    location.save()
                    task_logger.info('Sending notification')
                    unreachable_notification(resource)

                else:
                    ping_device(resource, NTD['Ping Device'])
                    resource_qs.update(
                        ping_count=F('ping_count') + 1
                    )
            else:
                pass


class Command(BaseCommand):
    help = 'Get unreachable agents'

    def handle(self, *args, **options):
        get_unreachables_bg(self)
        msg = 'Successfully Finished get unreachable....'
        task_logger.info(msg)
        self.stdout.write(self.style.SUCCESS(msg))

