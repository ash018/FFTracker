from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import AssignmentSerializer, CommentSerializer
from .helpers import *
from .filters import assignment_filter

from apps.billing.helpers import check_task_quantity, \
    adjust_task_quantity, check_subscription
from apps.common.helpers import get_paginated
from apps.notification.config import NOTIFICATION_DICT as NTD
from apps.notification.transmitters import assignment_notification


class AssignmentViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk, format=None):
        """
        Sample response:
        ---
            {
                'title': 'texts...',
                'description': 'texts...',
                'manager': 22,
                'assignee_list': [12, 13],
                'status': 2, // (1, Remaining), (2, In progress),(3, Complete),(4, Cancelled),

                'org': 222,

                'deadline': "2019-03-11T07:07:24.000000+00:00",
                'custom_fields': {json field},

                'comment_list': [
                    {
                        'id': 233,
                        'timestamp': date_str,
                        'text': 'some text..',
                        'attachments': ['url1..', 'url2..']
                        'user': 'Name',
                        'image': 'url..',
                    },...
                ],

                'manager': 'manager1',
                'manager_id': 12,
                'manager_image':'url..',

                'assignee': 'assignee',
                'assignee_id': 23,
                'assignee_image': 'url..',

                'assignee_list': [
                    {
                        'id': 23,
                        'name': 'user1',
                        'image': 'url...',
                    },
                    {
                        'id': 24,
                        'name': 'user2',
                        'image': 'url...',
                    },....
                ]

            }

        """
        if Assignment.objects.filter(id=pk).exists():
            assignment = Assignment.objects.select_related(
                'manager', 'assignee'
            ).prefetch_related(
                'comment_set'
            ).get(id=pk)
            # self.check_object_permissions(request, assignment)
            task_data = get_assignment_data(assignment)
            return Response(task_data, status=200)
        return Response({'msg': 'Assignment not found!'}, status=400)

    def list(self, request, format=None):
        """
        Query parameters:
        ---
            status:
                type: int
                required: No
                choices:
                    (1, 'Remaining'),
                    (2, 'In progress'),
                    (3, 'Complete'),
                    (4, 'Cancelled'),
            assignee_id:
                type: int
                required: No
            manager_id:
                type: int
                required: No
            token:
                type: str
                required: No

        Sample response:
        ---
            [
                {
                    'id': 12,
                    'title': 'texts...',
                    'deadline': "2019-03-11T07:07:24.000000+00:00",
                    'status': 2, // (1, Remaining), (2, In progress),(3, Complete),(4, Cancelled),


                    'manager': 'manager1',
                    'manager_id': 12,
                    'manager_image':'url..',

                    'assignee': 'assignee',
                    'assignee_id': 23,
                    'assignee_image': 'url..',


                    'assignee_list': [
                        {
                            'id': 12,
                            'name': 'user1',
                            'image': 'url...',
                        },
                        {
                            'id': 13,
                            'name': 'user2',
                            'image': 'url...',
                        },....
                    ]

                },...
            ]

        """
        assignment_qf = assignment_filter(request)
        offset = 0
        limit = 50

        assignment_qs = get_assignment_qs(
            assignment_qf
        )[offset: offset + limit]

        assignment_list = get_assignment_list(
            assignment_qs
        )

        return Response(assignment_list, status=200)

    def create(self, request, format=None):
        """
        Sample Submit:
        ---
            {
                'title': 'texts...',
                'description': 'texts...',
                'manager': 22,
                'assignee': 12,
                'assignee_list': [12, 13],
                'org': 222,

                'deadline': "2019-03-11T07:07:24.000000+00:00",
                'custom_fields': {json field}

            }
        """
        if not check_subscription(request):
            return Response({'msg': 'Payment is due!'}, status=402)
        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            instances = 1
            if not check_task_quantity(request, instances):
                return Response({'msg': 'Task limit exceeded!'}, status=402)
            # adjust task count

            assignment = serializer.create_assignment(serializer.validated_data, request)
            adjust_task_quantity(request, instances)
            data = get_assignment_data(assignment)
            return Response(data, status=201)
        return Response(serializer.errors, status=400)

    def partial_update(self, request, pk, format=None):
        """
        Sample Submit:
        ---
            {
                'title': 'texts...',
                'description': 'texts...',
                'manager': 22,
                'assignee': 12,
                'assignee_list': [12, 13],
                'org': 222,

                'status': 2, // (1, Remaining), (2, In progress),(3, Complete),(4, Cancelled),

                'deadline': "2019-03-11T07:07:24.000000+00:00",
                'custom_fields': {json field}

            }
        """

        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            if Assignment.objects.filter(id=pk).exists():
                assignment = Assignment.objects.get(id=pk)
                assignment = serializer.update_assignment(
                    assignment, serializer.validated_data, request
                )
                data = get_assignment_data(assignment)
                return Response(data, status=200)
            return Response({'detail': 'Assignment not found!'}, status=400)
        return Response(serializer.errors, status=400)


class PaginatedAssignments(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        assignment_qf = assignment_filter(request)

        assignment_qs = get_assignment_qs(
            assignment_qf
        )

        data = get_paginated(
            assignment_qs,
            request,
            get_assignment_list
        )
        return Response(data, status=200)


class AddComment(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Sample Submit:
        ---
            {
                'text': 'some text..',
                'attachments': ['url1', 'url2',..],
                'user': 22,
                'assignment': 2
            }
        """
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.create(serializer.validated_data)
            user = request.user
            assignment = comment.assignment
            assignment_notification(
                assignment,
                NTD['New Comment'],
                user,
                user.full_name + ' commented on assignment: ' + assignment.title
            )
            data = {
                'detail': 'OK'
            }
            return Response(data, status=201)
        return Response(serializer.errors, status=400)


class UpdateProgress(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk, format=None):
        """
        Sample Submit:
        ---
            {
                'progress': 50,
            }
        """
        user = request.user
        progress = request.data.get('progress', False)
        if not progress:
            return Response({'detail': 'Provide progress value!'}, status=400)
        assignment_qs = Assignment.objects.filter(
            id=pk
        )

        if len(assignment_qs) < 1:
            return Response({'detail': 'Assignment not found!'}, status=400)
        assignment = assignment_qs[0]
        assignment.progress = progress
        assignment.save()

        text = user.full_name + ' updated the progress of assignment: ' + assignment.title
        assignment_notification(assignment, NTD['Assignment Modified'], user, text)

        return Response({'msg': 'OK'}, status=200)


