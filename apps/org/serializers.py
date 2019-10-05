from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.utils import timezone
from rest_framework.exceptions import NotAcceptable, PermissionDenied
from .helpers import invalid_office_time

from apps.org.models import Organization


def trial_cycle():
    return timezone.now() + timezone.timedelta(days=15)


class OrgSerializer(ModelSerializer):

    class Meta:
        model = Organization
        fields = [
            'org_name',
            'address',
            'day_start',
            'day_end',
            'location_interval',
            'logo',
            'min_work_hour_p',
            'weekend',
            'tracking_enabled',
        ]

    def validate(self, data):
        """
        Check that office timing is valid.
        """
        if invalid_office_time(data):
            raise NotAcceptable(detail='Invalid Office time!')
        return data

    def org_update(self, org, validated_data):
        org = self.update(org, validated_data)
        org.org_set = True
        org.save()
        return org


