from django.db.models import Q
from background_task import background
import logging

from apps.location.models import Location
from apps.task.models import Task
from apps.task.helpers import get_task_list
from apps.user.models import User
from apps.location.helpers import *
from .config import get_address

task_logger = logging.getLogger('task_logger')


@background(schedule=2)
def upload_offline_locations(agent_id, locations, mac):

    agent = User.objects.get(id=agent_id)
    task_logger.info('Offline location upload for: ' + agent.username)
    for loc in locations:
        try:
            address = get_address(loc['point']['lat'], loc['point']['lng'])
            location = Location(
                org=agent.org,
                point=loc['point'],
                timestamp=get_datetime(loc['timestamp']),
                event=loc['event'],
                agent=agent,
                address=address,
                mac=mac
            )
            active_task_id = agent.userstate.active_task_id
            if active_task_id:
                location.on_task_id = active_task_id
            location.save()
            # print(location)
        except Exception as e:
            task_logger.debug(str(e))
            pass


def get_agent_locations(request):
    manager = request.user
    agent_id = request.query_params.get('agent_id', False)
    agent_filter = Q(parent=manager) & Q(is_active=True)
    if agent_id:
        agent_filter &= Q(id=agent_id)
    agents = User.objects.filter(agent_filter)
    location_list = []
    for agent in agents:
        if Location.objects.filter(agent=agent).exists():
            location = Location.objects.filter(agent=agent).order_by('-timestamp')[0]
            location_list.append(get_location_details(location))
    return location_list


def get_resource_history(agent, date):
    date_obj = timezone.datetime.strptime(date, '%Y-%m-%d')

    location_qs = Location.objects.select_related(
        'agent', 'on_task'
    ).filter(
        Q(agent=agent) &
        Q(date=date_obj.date())
    )

    task_qs = Task.objects.defer(
        'creator', 'ts_start', 'ts_finish', 'custom_fields',
        'images', 'point_finish', 'point_start',
    ).select_related(
        'manager'
    ).prefetch_related(
        'agent_list'
    ).filter(
        Q(agent_list=agent) &
        Q(date=date_obj.date())
    ).order_by('-deadline').distinct()

    location_list = []
    task_list = get_task_list(task_qs)
    for loc in location_qs:
        location_list.append(get_location_details(loc))

    return location_list, task_list
