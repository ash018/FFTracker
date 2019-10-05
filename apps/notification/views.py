from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .helpers import *
from apps.common.helpers import get_paginated
from .serializers import NotificationSerializer
from .config import send_notification


class Notifications(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Query Parameters:
        ---
            status:
                type: int
                required: Yes
                choices:
                    'Deadline crossed': 0,
                    'Unreachable': 1,
                    'Task cancelled': 2,
                    'Task postponed': 3,
                    'Near Deadline': 4,
                    'New Task': 5,
                    'SOS': 6,
                    'Alert': 7,
                    'Task started': 8,
                    'Task finished': 9,
                    'Assignment Created': 10,
                    'Assignment Modified': 11,
                    'New Comment': 12,

        Sample response:
        ---
            [
                {
                    'ntf_id': 23,
                    'type': 3,
                    'point': {},

                    'task_id': 12,
                    'task_title': 'Visit',

                    'agent_id': 34,
                    'agent_name': 'Name',

                    'assignment_id': 44,
                    'assignment_title': 'Assignment 1',

                    'timestamp': str(ntf.timestamp),
                    'text': '',
                    'images': ntf.images,
                    'checked': ntf.checked,
                },....
            ]
        """

        user = request.user
        ntf_type = request.query_params.get('ntf_type', False)
        ntf_qf = Q(recipient=user)
        if ntf_type:
            ntf_qf &= Q(type=NTD[ntf_type])

        ntf_qs = Notification.objects.filter(ntf_qf).order_by('-timestamp')
        ntf_data = []
        for ntf in ntf_qs:
            ntf_data.append(get_notification_content(ntf))

        return Response(ntf_data, status=status.HTTP_200_OK)


class PaginatedNotifications(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Sample response:
        ---
            {
                'limit': 10,
                'offset': 20,
                'count': 101,
                'next': 'limit=5&offset=30',
                'prev': 'limit=5&offset=10',
                'results': [
                    {
                        'ntf_id': 23,
                        'type': 3,
                        'point': {},
                        'address': '',

                        'task_id': 12,
                        'task_title': 'Visit',

                        'agent_id': 34,
                        'agent_name': 'Name',

                        'assignment_id': 44,
                        'assignment_title': 'Assignment 1',

                        'timestamp': str(ntf.timestamp),
                        'text': 'new notification..',
                        'images': [],
                        'checked': false,
                        },...
                ]
            }
        """
        user = request.user
        ntf_type = request.query_params.get('ntf_type', False)
        ntf_qf = Q(recipient=user)
        if ntf_type:
            ntf_qf &= Q(type=NTD[ntf_type])

        ntf_qs = Notification.objects.filter(
            ntf_qf
        ).order_by('-timestamp')

        data = get_paginated(
            ntf_qs,
            request,
            get_ntf_list
        )
        return Response(data, status=200)


class SOSCreate(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Sample response:
        ---
            {
                'point': {'lat': 23.780926, 'lng': 90.422858},
                'text': 'New issue..',
                'type': 2,
                'agent': 23,
                'images': ['url1..', 'url2..'],
            },....
        """
        user = request.user
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            address = ''
            if serializer.validated_data.get('point'):
                point = serializer.validated_data['point']
                address = get_address(point['lat'], point['lng'])
            recipients_qs = user.get_family()
            for rcpt in recipients_qs:
                ntf = serializer.create(serializer.validated_data)
                ntf.recipient = rcpt
                ntf.address = address
                ntf.save()
                send_notification(ntf)

            data = {
                'msg': 'Created!'
            }
            return Response(data, status=201)

        return Response(serializer.errors, status=400)


class GetCount(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Sample response:
        ---
            {
                'unchecked': 1,
                'total': 10
            }
        """

        user = request.user
        ntf_qs = Notification.objects.filter(Q(recipient=user))
        total = ntf_qs.count()
        unchecked = ntf_qs.filter(Q(checked=False)).count()
        data = {
            'unchecked': unchecked,
            'total': total
        }

        return Response(data, status=status.HTTP_200_OK)


class SetCount(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk, format=None):
        """
        Sample response:
        ---
            {
                'unchecked': 1,
                'total': 10
            }
        """

        user = request.user
        Notification.objects.filter(id=pk).update(
            checked=True
        )

        ntf_qs = Notification.objects.filter(Q(recipient=user))
        total = ntf_qs.count()
        unchecked = ntf_qs.filter(Q(checked=False)).count()
        data = {
            'unchecked': unchecked,
            'total': total
        }

        return Response(data, status=status.HTTP_200_OK)


class MarkAllRead(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        user_id = request.user.id
        Notification.objects.filter(Q(recipient_id=user_id)).update(
            checked=True
        )

        data = {
            'msg': 'OK'
        }

        return Response(data, status=status.HTTP_200_OK)


