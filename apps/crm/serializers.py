from rest_framework.serializers import ModelSerializer
# from rest_framework import serializers
# from django.core.exceptions import PermissionDenied
# from rest_framework.exceptions import NotAcceptable, ValidationError

from .models import Lead


class LeadSerializer(ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            'name',
            'phone',
            'email',

            'company_name',
            'domain_choice',
            'employee_count',
        ]
