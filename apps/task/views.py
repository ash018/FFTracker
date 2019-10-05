from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import TaskTemplate
from apps.task.serializers import TaskSerializer, \
    CTSAgentSerializer, CTSManagerSerializer, TaskTemplateSerializer
from apps.user.permissions import CanUpdateTask, IsAgentOfTask, is_manager, is_agent
from apps.task.helpers import *
from .filters import task_filter
from apps.common.helpers import get_paginated
from apps.location.config import get_address
from apps.task.config import TASK_STATUS_DICT
from apps.billing.helpers import check_task_quantity, adjust_task_quantity, check_subscription


class TaskViewSetManager(viewsets.ViewSet):
    permission_classes = (CanUpdateTask,)

    def retrieve(self, request, pk, format=None):
        """
        Sample response:
        ---
            {
                'id': 11,
                'title': 'Title',
                'point': {'lat': 23.780926, 'lng': 90.422858},
                'status': 0,
                'start': datetime,
                'deadline': datetime,
                "images": ['url1..', 'url2..'],

                'task_type': 'Doctors visit',
                'agent_list': [50, 51],
                'manager': 'name',
                'custom_fields': [],
                'address': 'address'
            }

        """
        is_manager(request)
        task_qs = Task.objects.select_related(
            'manager'
        ).prefetch_related(
            'agent_list'
        ).filter(id=pk)
        if len(task_qs) < 1:
            return Response({'detail': 'Task not found!'}, status=400)
        task = task_qs[0]
        self.check_object_permissions(request, task)
        task_data = get_task_details(task)
        # print(task_data)
        return Response(task_data, status=200)

    def list(self, request, format=None):
        """
        Query parameters:
        ---
            status:
                type: int
                required: No
                choices:
                    (0, 'Unassigned'),
                    (1, 'Remaining'),
                    (2, 'In progress'),
                    (3, 'Complete'),
                    (4, 'Cancelled'),
                    (5, 'Postponed'),
            delayed:
                type: bool
                required: no
            task_type:
                type: string
                required: No
            deadline:
                type: timestamp
                required: No
            agent_id:
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
                    'id': task.id,
                    'title': task.title,
                    'status': task.status,
                    'deadline': str(task.deadline),
                    'task_type': task.task_type,
                    'agent_list': [],
                    'manager': 'Manager',
                    'manager_id': 12,
                    'delayed': false,
                    'address': task.address,
                    'point': {},
                },...
            ]

        """
        is_manager(request)
        task_manager_qf = task_filter(request)
        # paginator = LimitOffsetPagination
        offset = 0
        limit = DEF_LIMIT

        task_obj_list = task_list_qs(task_manager_qf)[offset: offset + limit]
        task_list = get_task_list(task_obj_list)

        return Response(task_list, status=200)

    def create(self, request, format=None):
        """
        Sample submit:
        ---
            {
                task_type: 'Doctor visit',
                start: "2019-03-11T07:07:24.000000+00:00",
                deadline: "2019-03-11T07:07:24.000000+00:00",
                "images": ['url1..', 'url2..'],
                point: {'lat': 23.780926, 'lng': 90.422858},
                address: 'Dhaka, Bangladesh',
                image_required: false,
                attachment_required: true,
                org: 111,
                manager: 10,
                agent_list: [1, 2, 3,..]
                custom_fields: {},
                instances: 1,
            }

        Sample response:
        ---
            {
                'ids': [2, 3,..]
            }
        """
        # is_manager(request)
        if not check_subscription(request):
            return Response({'msg': 'Payment is due!'}, status=402)
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():

            instances = int(serializer.validated_data['instances'])

            if not check_task_quantity(request, instances):
                return Response({'msg': 'Task limit exceeded!'}, status=402)
            # adjust task count
            adjust_task_quantity(request, instances)

            task_list = serializer.create_task(serializer.validated_data, request)
            data = {
                'ids': task_list
            }
            return Response(data, status=201)
        return Response(serializer.errors, status=400)

    def partial_update(self, request, pk, format=None):
        """
        Sample submit:
        ---
            {
                task_type: 'Doctor visit',
                start: "2019-03-11T07:07:24.000000+00:00",
                deadline: "2019-03-11T07:07:24.000000+00:00",
                "images": ['url1..', 'url2..'],
                point: {'lat': 23.780926, 'lng': 90.422858},
                address: 'Dhaka, Bangladesh',
                image_required: false,
                attachment_required: true,
                org: 111,
                manager: 10,
                agent_list: [1, 2, 3,..]
                custom_fields: {},
                instances: 1,
            }


        Sample response:
        ---
            {
                'id': 2
            }
        """
        is_manager(request)
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task_qs = Task.objects.filter(id=pk)
            if len(task_qs) < 1:
                return Response({'detail': 'Task not found!'}, status=400)
            task = task_qs[0]
            self.check_object_permissions(request, task)
            with transaction.atomic():
                task = serializer.update_task(serializer.validated_data, task)
                task.delayed = False
                task.save()
            data = {
                'id': task.id
            }
            return Response(data, status=200)
        return Response(serializer.errors, status=400)


class PaginatedTasks(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        # is_manager(request)

        """
        Query parameters:
        ---
            status:
                type: int
                required: No
                choices:
                    (0, 'Unassigned'),
                    (1, 'Remaining'),
                    (2, 'In progress'),
                    (3, 'Complete'),
                    (4, 'Cancelled'),
                    (5, 'Postponed'),
            delayed:
                type: bool
                required: no
            task_type:
                type: string
                required: No
            deadline:
                type: timestamp
                required: No
            agent_id:
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
            {
                'limit': 10,
                'offset': 20,
                'count': 101,
                'next': 'limit=5&offset=30',
                'prev': 'limit=5&offset=10',
                'results': [
                    {
                        'id': task.id,
                        'title': task.title,
                        'status': task.status,
                        'deadline': str(task.deadline),
                        'task_type': task.task_type,
                        'agent_list': [],
                        'manager': 'Manager',
                        'manager_id': 12,
                        'delayed': false,
                        'address': task.address,
                        'point': {},
                    },...
                ]
            }
        """

        task_qf = task_filter(request)
        data = get_paginated(
            task_list_qs(task_qf),
            request,
            get_task_list
        )
        return Response(data, status=200)


class ExportTasks(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Query parameters:
        ---
            status:
                type: int
                required: No
                choices:
                    (0, 'Unassigned'),
                    (1, 'Remaining'),
                    (2, 'In progress'),
                    (3, 'Complete'),
                    (4, 'Cancelled'),
                    (5, 'Postponed'),
            delayed:
                type: bool
                required: no
            task_type:
                type: string
                required: No
            deadline:
                type: timestamp
                required: No
            agent_id:
                type: int
                required: No
            manager_id:
                type: int
                required: No

        Sample response:
        ---
            [
                {
                    'id': task.id,
                    'title': task.title,
                    'status': task.status,
                    'deadline': str(task.deadline),
                    'task_type': task.task_type,
                    'agent_list': [],
                    'manager': 'Manager',
                    'manager_id': 12,
                    'delayed': false,
                    'address': task.address,
                    'point': {},
                },...
            ]

        """
        task_qf = task_filter(request)
        task_qs = Task.objects.defer(
            'creator', 'custom_fields',
            'point_finish', 'point_start',
        ).select_related(
            'manager'
        ).prefetch_related(
            'agent_list'
        ).filter(
            task_qf
        ).order_by('-deadline').distinct()

        task_list = get_task_list(task_qs)
        return Response(task_list, status=200)


class ChangeTaskManager(GenericAPIView):
    permission_classes = (CanUpdateTask,)
    serializer_class = CTSManagerSerializer

    def post(self, request, pk, format=None):
        """
        Parameter details:
        ---
            status:
                type: int
                required: Yes
                choices:
                        (4, 'Cancelled'),
                        (5, 'Postponed'),
        """
        is_manager(request)
        if not check_subscription(request):
            return Response({'msg': 'Payment is due!'}, status=402)
        serializer = CTSManagerSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            task_qs = Task.objects.filter(id=pk)
            if len(task_qs) < 1:
                return Response({'detail': 'Task not found!'}, status=400)
            task = task_qs[0]
            with transaction.atomic():
                serializer.cts_manager(task, serializer.validated_data)
            return Response({'msg': 'OK'}, status=200)
        return Response(serializer.errors, status=400)


class TaskViewSetAgent(viewsets.ViewSet):
    permission_classes = (IsAgentOfTask,)

    def retrieve(self, request, pk, format=None):
        """
        Sample response:
        ---
            {
                'id': 11,
                'title': 'Title',
                'point': {'lat': 23.780926, 'lng': 90.422858},
                'status': 0,
                'start': datetime,
                'deadline': datetime,
                "images": ['url1..', 'url2..'],

                'task_type': 'Doctors visit',
                'agent_list': [50, 51],
                'manager': 'name',
                'custom_fields': [],
                'address': 'address'
            }

        """
        task_qs = Task.objects.select_related(
            'manager'
        ).prefetch_related(
            'agent_list'
        ).filter(id=pk)
        if len(task_qs) < 1:
            return Response({'detail': 'Task not found!'}, status=400)
        task = task_qs[0]
        self.check_object_permissions(request, task)
        task_data = get_task_details(task)
        return Response(task_data, status=200)

    def list(self, request, format=None):
        """
        Query parameters:
        ---
            status:
                type: int
                required: No
                choices:
                    (0, 'Unassigned'),
                    (1, 'Remaining'),
                    (2, 'In progress'),
                    (3, 'Complete'),
                    (4, 'Cancelled'),
                    (5, 'Postponed'),
            delayed:
                type: bool
                required: no
            task_type:
                type: string
                required: No
            deadline:
                type: timestamp
                required: No
        Sample response:
        ---
            {
                [
                    {
                        'title': 'Task_test1',
                        'status': 1,
                        'deadline': datetime,
                        'task_type': 'Visit1',
                        'address': '',
                        'agent_list': [50, 51]
                    },...
                ]
            }

        """
        agent_task_qf = task_filter(request)
        # paginator = LimitOffsetPagination
        offset = 0
        limit = DEF_LIMIT

        task_obj_list = task_list_qs(agent_task_qf)[offset: offset + limit]
        task_list = get_task_list(task_obj_list)

        return Response(task_list, status=200)

    def create(self, request, format=None):
        """
        Sample submit:
        ---
            {
                task_type: 'Doctor visit',
                start: "2019-03-11T07:07:24.000000+00:00",
                deadline: "2019-03-11T07:07:24.000000+00:00",
                "images": ['url1..', 'url2..'],
                point: {'lat': 23.780926, 'lng': 90.422858},
                address: 'Dhaka, Bangladesh',
                image_required: false,
                attachment_required: true,
                org: 111,
                manager: 10,
                agent_list: [1, 2, 3,..]
                custom_fields: {},
                instances: 1,
            }

        Sample response:
        ---
            {
                'ids': [2, 3,..]
            }
        """
        if not check_subscription(request):
            return Response({'msg': 'Payment is due!'}, status=402)
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            instances = int(serializer.validated_data['instances'])
            if not check_task_quantity(request, instances):
                return Response({'msg': 'Task limit exceeded!'}, status=402)
            # adjust task count
            adjust_task_quantity(request, instances)

            task_list = serializer.create_task(serializer.validated_data, request)
            data = {
                'ids': task_list
            }
            return Response(data, status=201)
        return Response(serializer.errors, status=400)

    def partial_update(self, request, pk, format=None):
        """
        Parameter details:
        ---
            status:
                type: int
                required: Yes
                choices:
                        (2, 'In progress'),
                        (3, 'Complete'),
                        (4, 'Cancelled'),
                        (5, 'Postponed'),
            event_point:
                type: json object
                example: {'lat': 23.780926, 'lng': 90.422858}
                required: Yes
            custom_fields:
                type: json object
                general fields: {
                    'image_urls': [{url: 'link1', point: {lat/lng}}, {url: 'link2', point: {lat/lng}}, ..], // If image is required in complete task
                    'attachment_urls': ['link1', 'link2', ..], // If attachment is required in complete task
                    'reason': 'string', // If task is cancelled or postponed
                }
        """
        if not check_subscription(request):
            return Response({'msg': 'Payment is due!'}, status=402)
        serializer = CTSAgentSerializer(data=request.data)
        if serializer.is_valid():
            task_qs = Task.objects.filter(id=pk)
            if len(task_qs) < 1:
                return Response({'msg': 'Task not found!'}, status=400)
            task = task_qs[0]
            self.check_object_permissions(request, task)
            serializer.cts_agent(task, serializer.validated_data, request)
            return Response({'msg': 'OK'}, status=200)
        return Response(serializer.errors, status=400)


class AddressFromPoint(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Parameter details:
        ---
            point:
                type: json object
                example: {'lat': 23.780926, 'lng': 90.422858}
                required: Yes

        """
        point = request.data.get('point', False)
        if point:
            address = get_address(point['lat'],
                                  point['lng'])
            return Response({'address': address}, status=200)
        return Response({'msg': 'No point found!'}, status=400)


class SelfAssignTask(APIView):
    permission_classes = (IsAgentOfTask,)

    def post(self, request, pk, format=None):
        """
        Parameter details:
        ---
            pk:
                type: int
                required: Yes
        """
        # is_agent(request)
        if not check_subscription(request):
            return Response({'msg': 'Payment is due!'}, status=402)

        if Task.objects.filter(id=pk):
            task = Task.objects.get(id=pk)
            self.check_object_permissions(request, task)
            agent = request.user
            if agent not in task.agent_list.all():
                task.agent_list.add(agent)
                task.status = TASK_STATUS_DICT['Remaining']
                task.save()
                return Response({'msg': 'OK'}, status=200)
            return Response({'msg': 'Added already!'}, status=200)
        return Response({'msg': 'Task not found!'}, status=400)


class TaskTemplateViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, )

    def retrieve(self, request, pk, format=None):
        """
        Sample Response:
        ---
            {
                'id': 1,
                'task_type': 'My task 1',
                'task_fields': {},
            }


        """
        # is_manager(request)
        # manager = request.user

        if TaskTemplate.objects.filter(id=pk).exists():
            task_template = TaskTemplate.objects.get(id=pk)
            task_template_details = get_template_data(task_template)
            return Response(task_template_details, status=200)
        resp = {'detail': "Template not found."}
        return Response(resp, status=400)

    def list(self, request, format=None):
        """
        Sample Response:
        ---
            [
                {
                    'id': 1id,
                    'task_type': 'My task 1',
                    'task_fields': {},
                },
                {
                    'id': 2,
                    'task_type': 'My task 2',
                    'task_fields': {},
                }
            ]


        """
        # is_manager(request)
        user = request.user
        qcommon_templates = Q(org=user.org)
        templates = TaskTemplate.objects.filter(qcommon_templates)
        template_list = []
        for temp in templates:
            template_list.append(get_template_data(temp))

        return Response(template_list, status=200)

    def create(self, request, format=None):
        """
        Sample Submit:
        ---
            {
                'user': user_id,
                'org': org_id,
                'task_type': 'my template',
                'task_fields': {},
            }
        """
        is_manager(request)

        serializer = TaskTemplateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'OK'}, status=201)
        return Response(serializer.errors, status=400)

    def partial_update(self, request, pk, format=None):
        """
        Sample Submit:
        ---
            {
                'user': user_id,
                'org': org_id,
                'task_type': 'my template',
                'task_fields': {},
            }
        """
        is_manager(request)
        template = TaskTemplate.objects.get(id=pk)

        serializer = TaskTemplateSerializer(template, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'OK'}, status=200)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk, format=None):
        is_manager(request)
        if TaskTemplate.objects.filter(id=pk):
            task_template = TaskTemplate.objects.get(id=pk)
            task_template.delete()
            return Response({'msg': 'OK'}, status=200)
        resp = {'detail': "Template not found."}
        return Response(resp, status=400)
