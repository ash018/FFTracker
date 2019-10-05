from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.exceptions import NotAcceptable
from django.db import transaction
from .helpers import *

from apps.task.config import TASK_STATUS_DICT as TSD
from apps.notification.transmitters import attendance_notification

from apps.task.models import Task
from apps.user.models import User
from apps.state.models import UserState

utc = pytz.UTC


class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = [
            'agent',
            'event',
            'point',
            'on_task',
            'mac',
        ]

    def upload_location(self, validated_data, request):
        agent = request.user
        agent_qs = User.objects.filter(id=agent.id)
        presence = agent.is_present
        remaining_task = Task.objects.filter(
            Q(agent_list=agent) &
            Q(status=TSD['In progress'])
        ).exists()
        loc_reply = None

        with transaction.atomic():
            loc = self.create(validated_data)
            loc.agent = agent
            loc.org = agent.org

            if presence:
                loc.on_task_id = agent.userstate.active_task_id
            address = get_address(loc.point['lat'], loc.point['lng'])
            loc.address = address
            loc.save()
            event_timestamp = loc.timestamp

            UserState.objects.filter(
                Q(user=agent)
            ).update(last_location=loc)

            # invalid_upload = not presence and loc.event != EVENT_DICT['To Online']
            # cur_device = agent.userstate.current_device
            # invalid_device = cur_device and loc.mac != cur_device.mac

            if not presence and loc.event != EVENT_DICT['To Online']:
                msg = 'invalid_upload'
                raise NotAcceptable(detail=msg)

            if loc.event == EVENT_DICT['To Online']:
                if presence:
                    msg = 'Already present!'
                    raise NotAcceptable(detail=msg)

                exec_online_event(user=agent, entry_timestamp=event_timestamp)
                presence = True
                attendance_notification(agent, presence)

            if loc.event == EVENT_DICT['To Offline']:
                # if remaining_task:
                #     msg = 'Task is in progress!'
                #     raise NotAcceptable(detail=msg)

                exec_offline_event(user=agent, exit_timestamp=event_timestamp)
                presence = False
                attendance_notification(agent, presence)

            agent_qs.update(
                is_working=remaining_task,
                is_awol=False,
                is_present=presence,
                ping_count=0
            )

            loc_reply = {
                'presence': presence,
                'location_interval': agent.org.location_interval,
            }
        return loc_reply
