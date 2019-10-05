from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from apps.billing.models import Payment


class BkashPaymentSerializer(ModelSerializer):

    class Meta:
        model = Payment
        fields = [
            'gateway',
            'vendor_uid',
            'payment_uid',
            'amount',
            'bill_type',
            'extra_tasks',
            'new_agents',
        ]

        extra_kwargs = {
            'vendor_uid': {'validators': []},
        }


class SSLCreateSerializer(serializers.Serializer):

    amount = serializers.FloatField(required=True)
    gateway = serializers.FloatField(required=False)
    bill_type = serializers.IntegerField(required=True)
    extra_tasks = serializers.IntegerField(required=True)
    new_agents = serializers.IntegerField(required=True)


class SSLExecuteSerializer(serializers.Serializer):

    class Meta:
        model = Payment
        fields = [
            'gateway',
            'vendor_uid',
            'amount',
            'bill_type',
            'extra_tasks',
            'new_agents',
        ]
