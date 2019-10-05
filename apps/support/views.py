from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from apps.user.permissions import is_organizer
from .models import CustomerSupport
from .serializers import CustomerSupportSerializer
from .helpers import *
from apps.user.models import User


class CustomerSupportViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk, format=None):
        """

        Sample response:
        ---
            {
                'id': 1,
                'subject': 'subject',
                'description': 'some description...',
                'date_created': datetime str,
                'status': 1
            }

        """
        if CustomerSupport.objects.filter(id=pk):
            supp = CustomerSupport.objects.get(id=pk)
            supp_details = get_supp_details(supp)
            # print(supp_details)
            return Response(supp_details, status=200)
        return Response({'msg': 'Location not found!'}, status=400)

    def list(self, request, format=None):
        """

        Sample response:
        ---
            {

                {
                    'id': 1,
                    'subject': 'subject',
                    'description': 'some description...',
                    'date_created': datetime,
                    'status': 1
                },
                {
                    'id': 2,
                    'subject': 'subject',
                    'description': 'some description...',
                    'date_created': datetime,
                    'status': 2
                },
                ..........
            }


        """
        user = request.user

        supp_list = CustomerSupport.objects.filter(Q(user=user))

        supp_dict_list = get_supp_dict_list(supp_list)

        return Response(supp_dict_list, status=200)

    def create(self, request, format=None):
        """

        Sample submit:
        ---
            {
                'subject': 'subject',
                'description': 'some description...',
            }

        """
        # is_organizer(request)
        organizer = request.user
        serializer = CustomerSupportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.support_create(serializer, organizer)
            data = {
                'msg': 'OK'
            }
            return Response(data, status=201)

        return Response(serializer.errors, status=400)

    def destroy(self, request, pk, format=None):
        # is_organizer(request)
        user = request.user
        supp = CustomerSupport.objects.get(id=pk)
        if supp.user == user or user.is_organizer:
            try:
                supp.delete()
                return Response({'msg': 'Support entry deleted!'}, status=200)
            except Exception as e:
                return Response({'msg': str(e)}, status=400)
        return Response({'msg': 'Permission denied!'}, status=403)
