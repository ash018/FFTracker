from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import LeadSerializer
from .helpers import get_url


class LeadSignupPage(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, format=None):
        context = {
            'signup_api': get_url(request, 'template/', 'signup_api'),
            'success_page': get_url(request, 'template/', 'success_page')
        }
        print(context)
        return render(request, 'crm/signup.html', {'context': context}, 200)


class SuccessPage(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, format=None):
        return render(request, 'crm/success.html', {}, 200)


class LeadSignupApi(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        """
        Sample submit:
        ---
            {
                "name": "name",
                "phone": "+88017XXXXXXXX",
                "email": "mail@usr.com",
                "employee_count": "100-500",
                "domain_choice": "Sales, Delivery and Logistics",
                "company_name": "Test company"
            }

        """

        serializer = LeadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response({'msg': 'Submitted!'}, status=201)

        return Response(serializer.errors, status=400)

