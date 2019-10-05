from django.utils import timezone
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import NotAcceptable, ValidationError

from .config import MSG_DICT as MSGD
from .models import Thread, Message
from apps.message.config import send_msg_payload, send_group_message
from .helpers import *


class ThreadSerializer(ModelSerializer):
    instances = serializers.IntegerField(default=1)

    class Meta:
        model = Thread
        fields = [
            'org',
            'name',
            'members',
            'admin',
        ]

    def create_thread(self, validated_data):
        thread = self.create(validated_data)
        thread.name += get_rand_str(8)
        thread.save()

        text = 'You joined the group ' + thread.name + \
               ' created by ' + thread.admin.full_name
        # TODO: set timestamp
        message = Message.objects.create(
            text=text,
            sender=thread.admin,
            type=MSGD['Group'],
            timestamp=timezone.now(),
            group=thread
        )
        resp = send_group_message(message, thread)
        return resp

    def update_thread(self, thread,  validated_data):
        thread = self.update(thread, validated_data)

        text = 'Group ' + thread.name + \
               ' has been modified by ' + thread.admin.full_name
        # TODO: set timestamp
        message = Message.objects.create(
            text=text,
            sender=thread.admin,
            type=MSGD['Group'],
            timestamp=timezone.now(),
            group=thread
        )
        resp = send_group_message(message, thread)
        return resp
