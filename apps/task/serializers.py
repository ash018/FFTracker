from django.utils import timezone
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import NotAcceptable, ValidationError
from apps.common.config import get_image_urls
from apps.task.helpers import *
from apps.notification.transmitters import task_change_notification, \
    new_task_notification
from apps.task.config import TASK_STATUS_DICT as TSD
from apps.task.models import TaskTemplate
from apps.notification.config import NOTIFICATION_DICT as NTD


class TaskSerializer(ModelSerializer):
    instances = serializers.IntegerField(default=1)

    class Meta:
        model = Task
        fields = [
            'instances',

            'title',
            'start',
            'deadline',
            'images',
            'image_required',
            'attachment_required',
            'task_type',

            'manager',
            'agent_list',

            'point',
            'address',
            'custom_fields',
        ]

    def create_task(self, validated_data, request):
        instances = int(validated_data['instances'])
        task_list = []
        validated_data.pop('instances')
        for idx in range(0, instances):
            task = self.create(validated_data)
            if len(task.agent_list.all()) > 0:
                task.status = TSD['Remaining']
            task.org = request.user.org
            task.creator = request.user
            task.date = task.deadline.date()
            task.save()
            new_task_notification(task)
            task_list.append(task.id)

        return task_list

    def update_task(self, validated_data, task):
        invalid_list = [TSD['In progress'], TSD['Cancelled'], TSD['Complete']]
        if task.status in invalid_list:
            raise NotAcceptable(detail='Task cannot be changed!')
        task = self.update(task, validated_data)
        if len(task.agent_list.all()) > 0:
            task.status = TSD['Remaining']
        else:
            task.status = TSD['Unassigned']
        task.save()
        return task


class CTSAgentSerializer(serializers.Serializer):
    status = serializers.IntegerField(required=True)
    custom_fields = serializers.JSONField(required=True)
    event_point = serializers.JSONField(required=True)

    def cts_agent(self, task, validated_data, request):
        task_status = int(validated_data['status'])
        custom_fields = validated_data['custom_fields']
        event_point = validated_data['event_point']
        agent = request.user
        image_urls = get_image_urls(request, task.id, 'task/')

        # print(custom_fields)
        # print(task_status)

        if agent not in task.agent_list.all():
            raise PermissionDenied
        if not agent.is_present:
            raise NotAcceptable(detail='Need to be online!')

        if task_status == TSD['In progress']:
            if not check_active_task(task):
                raise NotAcceptable(detail='Agent has in progress Task!')
            set_active_task(task)
            task.ts_start = timezone.now()
            task.point_start = event_point
            task_change_notification(agent, task, NTD['Task started'])

        elif task_status == TSD['Complete']:
            # TODO: Add other file types
            if len(image_urls) > 0:
                custom_fields['image_urls'] = image_urls
            if task.image_required and custom_fields['image_urls'] == '':
                raise NotAcceptable(detail='Please provide images!')
            if task.attachment_required and custom_fields['attachment_urls'] == '':
                raise NotAcceptable(detail='Please provide attachments!')

            unset_active_task(task)

            task.ts_finish = timezone.now()
            task.point_finish = event_point
            task_change_notification(agent, task, NTD['Task finished'])

        elif task_status == TSD['Cancelled']:
            # print(custom_fields)
            if 'reason' not in custom_fields:
                raise NotAcceptable(detail='Please provide a reason!')
            unset_active_task(task)
            task_change_notification(agent, task, NTD['Task cancelled'])
        elif task_status == TSD['Postponed']:
            # print(custom_fields)
            if custom_fields['reason'] == '':
                raise NotAcceptable(detail='Please provide a reason!')
            unset_active_task(task)
            task_change_notification(agent, task, NTD['Task postponed'])
        else:
            raise NotAcceptable(detail='Invalid task status: ' + str(task_status))
        # print('Task status', task_status)
        task.custom_fields = custom_fields
        task.status = task_status
        task.save()
        return task


class CTSManagerSerializer(serializers.Serializer):
    status = serializers.IntegerField(required=True)

    def cts_manager(self, task, validated_data):
        request = self.context['request']
        user = request.user
        if task.status == TSD['In progress']:
            raise NotAcceptable(detail='Task is in progress!')
        task_status = validated_data['status']

        if task_status == TSD['Cancelled']:
            unset_active_task(task)
            task_change_notification(user, task, NTD['Task cancelled'])
        elif task_status == TSD['Postponed']:
            unset_active_task(task)
            task_change_notification(user, task, NTD['Task postponed'])
        else:
            raise NotAcceptable
        task.status = task_status
        task.save()
        return task


class TaskTemplateSerializer(ModelSerializer):

    class Meta:
        model = TaskTemplate
        fields = [
            'user',
            'org',
            'task_type',
            'task_fields',
        ]
