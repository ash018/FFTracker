from datetime import datetime
import pytz
from django.utils import timezone
from django.db.models import Q

from .models import Location
from .config import EVENT_DICT, get_address

from apps.user.auth_helpers import get_username
from apps.report.config import ATTENDANCE_STATUS_DICT as ASD
from apps.report.models import AttendanceIndividual as ATI


utc = pytz.UTC


def get_datetime(date_time_str, time_format='%Y-%m-%d %H:%M:%S.%f'):
    ts = datetime.strptime(date_time_str, time_format)
    return utc.localize(ts)


def get_location_details(loc):
    location_detail = {
        'point': loc.point,
        'address': loc.address,
        'id': loc.agent.id,
        'username': get_username(loc.agent),
        'full_name': loc.agent.full_name,
        'task_id': loc.on_task_id if loc.on_task else None,
        'task_title': loc.on_task.title if loc.on_task else '',
        'event': loc.event,
        'timestamp': str(loc.timestamp),
        'presence': loc.agent.is_present,
        'image': loc.agent.image,
        'location_interval': loc.agent.org.location_interval,

    }
    return location_detail


def exec_online_event(user, entry_timestamp):
    ati_filter = Q(date=entry_timestamp.date()) & Q(user=user)
    ati_qs = ATI.objects.filter(ati_filter)
    if len(ati_qs):
        ati = ati_qs[0]
        if ati.status == ASD['Absent']:
            ati.status = ASD['Present']
            ati.init_entry_time = entry_timestamp
        ati.last_entry_time = entry_timestamp
        ati.save()
    else:
        late_arrival = False
        day_start = user.org.day_start
        entry_timestamp = entry_timestamp
        start_time = datetime.combine(entry_timestamp.date(), day_start)
        if entry_timestamp > utc.localize(start_time):
            late_arrival = True
        ati = ATI.objects.create(
            date=entry_timestamp.date(),
            user=user, org=user.org,
            late_arrival=late_arrival,
            status=ASD['Present'],
            init_entry_time=entry_timestamp,
            last_entry_time=entry_timestamp,
        )


def exec_offline_event(user, exit_timestamp):
    ati_filter = Q(date=exit_timestamp.date()) & Q(user=user)
    loc_filter = Q(date=exit_timestamp.date()) & Q(agent=user)
    ati_qs = ATI.objects.filter(ati_filter)
    if len(ati_qs):
        ati = ati_qs[0]
        ati.exit_time = exit_timestamp
        if not ati.work_hour:
            ati.work_hour = exit_timestamp - ati.last_entry_time
        else:
            ati.work_hour = ati.work_hour + (exit_timestamp - ati.last_entry_time)

        loc_qs = Location.objects.filter(loc_filter)
        loc_count = loc_qs.count()
        on_task_count = loc_qs.filter(Q(event=EVENT_DICT['On Task'])).count()
        if loc_count > 0:
            ati.task_hour_p = float(on_task_count / loc_count) * 100
        ati.save()
    else:
        pass
        # raise NotAcceptable(detail='Not present yet!')

