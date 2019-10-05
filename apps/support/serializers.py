from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.db.models import Q

from .models import CustomerSupport
from apps.user.models import User


class CustomerSupportSerializer(ModelSerializer):

    class Meta:
        model = CustomerSupport
        fields = [
            'subject',
            'description',
        ]

    def support_create(self, serializer, user):
        supp = serializer.create(serializer.validated_data)
        supp.user = user
        supp.org = user.org
        supp.save()
        return supp
