from rest_framework.views import APIView
from django.db.models import Sum
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.user.helpers import *
from apps.user.permissions import is_manager, is_organizer
from apps.user.serializers import AccountSerializerAdmin, AccountSerializerEmployee
from apps.task.views import get_task_list
from apps.user.filters import account_filter, resource_filter
from apps.user.auth_helpers import check_same_org
from apps.common.helpers import get_paginated
from apps.common.config import get_file_urls, get_image_urls
from apps.notification.helpers import get_unchecked_count
from apps.user.dict_extractors import get_profile_details, get_resource_details, \
    get_user_list, get_user_details, get_resource_list
from apps.billing.helpers import check_user_count, adjust_user_count, \
    check_subscription, adjust_subscription


class ProfileViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def retrieve(self, request, pk, format=None):
        """
        Response:
        ---
            {
                'id': 12,
                'username': 'username',
                'name': 'name1',
                'phone': '+88017XXXXXXXX',
                'image': 'url,
                'email': 'manager.email',
                'domain_choices': {},
                'domain': 2,
                'location_interval': 120,

                'org_id': 12,
                'oid': 'gp-121',
                'org_name': 'Grameenphone Ltd.',
                'day_start': time string,
                'day_end': time string,
                'org_set': false,

                'task_templates': {},
                'other_templates':{},

                'manager_id': 22,
                'manager_name': 'Manager',
                'manager_image': 'url....',

                'role': 2, // (0, Organizer), (1, Manager), (2, Agent)
                'packages': {},
                'package_info': {},
                'renew_needed': false,
                'has_password': false,
                'tracking_enabled': true,
            }
        """
        user_qs = User.objects.select_related(
            'org',
            'parent',
            'org__subscription',
            'org__subscription__current_usage'
        ).filter(id=pk)
        if len(user_qs) < 1:
            resp = {'detail': "User not found."}
            return Response(resp, status=400)
        user = user_qs[0]
        user_details = get_profile_details(user)
        # print(user)
        return Response(user_details, status=200)

    def partial_update(self, request, pk, format=None):
        """
        Domain Choices:
        ---
            'Sales': 0,
            'Delivery Service': 1,
            'Installment/Maintenance/Repair': 2,
            'Rent-a-car/Ride sharing': 3,
            'Security': 4,
            'Others': 5

        Sample Submit:
        ---
            {
                'full_name': 'user1',
                'email': 'email',
                'phone': '+88017XXXXXXXX',
                'domain': 2,
            }
        """

        is_manager(request)
        if User.objects.filter(id=pk).exists():
            manager = User.objects.get(id=pk)
            serializer = AccountSerializerEmployee(data=request.data)
            if serializer.is_valid():
                manager = serializer.update_user(manager, serializer.validated_data)
                data = get_profile_details(manager)
                return Response(data, status=200)
            return Response(serializer.errors, status=400)
        return Response({'msg': 'User not found!'}, status=400)


class UserAdminViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk, format=None):
        viewer = request.user
        user_qs = User.objects.select_related(
            'parent', 'org'
        ).filter(id=pk)
        if len(user_qs) < 1:
            resp = {'detail': "User not found."}
            return Response(resp, status=400)
        user = user_qs[0]
        check_same_org(user, viewer)
        user_details = get_user_details(user)
        # print(user)
        return Response(user_details, status=200)

    def list(self, request, format=None):
        """
        Query parameters:
        ---
            manager_id:
                type: int
                required: No

            role:
                type: int
                required: No
                choices: (1, Manager), (2, Agent), (0, Organizer)

            token:
                type: str
                required: No

        Sample Response:
        ---

            [
                {
                    'id': 222,
                    'username': 'username1',
                    'full_name': 'full_name',
                    'image': 'image_url..',
                    'designation': 'designation',
                    'phone': 'phone',
                    'manager_name': 'manager_name',
                    'manager_id': 23,
                    'manager_image': 'image_url..',
                    'manager_designation': 'designation',
                    'role': 1,
                },..
            ]


        """
        users_qs = account_filter(request)

        user_list = get_user_list(users_qs)

        return Response(user_list, status=200)

    def create(self, request, format=None):
        """
        Sample Submit:
        ---
            {
                'full_name': 'agent1',
                'username': 'username',
                'designation': 'DGM',
                'email': 'email',
                'role': 2, // (1, Manager), (2, Agent), (0, Organizer)
                'parent': 'manager_id',
                'phone': '+88017XXXXXXXX',
            }
        """
        is_organizer(request)
        if not check_user_count(request):
            resp = {
                'detail': 'Please purchase more accounts!'
            }
            return Response(resp, status=402)
        serializer = AccountSerializerAdmin(data=request.data)
        if serializer.is_valid():
            # manager = request.user
            user = serializer.create_user(serializer.validated_data, request)
            agent_details = get_profile_details(user)
            adjust_user_count(request)
            return Response(agent_details, status=201)
        data = {
            'detail': str(serializer.errors)
        }
        return Response(data, status=400)

    def partial_update(self, request, pk, format=None):
        """
        Sample Submit:
        ---
            {
                'full_name': 'agent1',
                'username': 'username',
                'email': 'email',
                'role': 2,
                'parent': 'manager_id',
                'phone': '+88017XXXXXXXX',
            }
        """
        viewer = request.user
        is_organizer(request)
        serializer = AccountSerializerAdmin(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(id=pk)
            check_same_org(user, viewer)
            user = serializer.update_user(user, serializer.validated_data)
            profile_details = get_profile_details(user)
            return Response(profile_details, status=200)
        data = {
            'detail': str(serializer.errors)
        }
        return Response(data, status=400)

    def destroy(self, request, pk, format=None):
        is_organizer(request)
        viewer = request.user
        user = User.objects.get(id=pk)
        check_same_org(user, viewer)
        try:
            delete_agent_data(user)
            adjust_user_count(request)
            return Response({'msg': 'User deleted!'}, status=200)
        except Exception as e:
            return Response({'msg': str(e)}, status=400)


class PaginatedAccounts(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Query parameters:
        ---
            manager_id:
                type: int
                required: No

            role:
                type: int
                required: No
                choices: (1, Manager), (2, Agent), (0, Organizer)

            token:
                type: str
                required: No

        Sample Response:
        ---

            [
                {
                    'id': 222,
                    'username': 'username1',
                    'full_name': 'full_name',
                    'image': 'image_url..',
                    'designation': 'designation',
                    'phone': 'phone',
                    'manager_name': 'manager_name',
                    'manager_id': 23,
                    'manager_image': 'image_url..',
                    'manager_designation': 'designation',
                    'role': 1,
                },..
            ]


        """
        users_qs = account_filter(request)
        data = get_paginated(
            users_qs,
            request,
            get_user_list
        )
        return Response(data, status=200)


class ExportAccounts(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Query parameters:
        ---
            manager_id:
                type: int
                required: No

            role:
                type: int
                required: No
                choices: (1, Manager), (2, Agent), (0, Organizer)

        Sample Response:
        ---

            [
                {
                    'id': 222,
                    'username': 'username1',
                    'full_name': 'full_name',
                    'image': 'image_url..',
                    'designation': 'designation',
                    'phone': 'phone',
                    'manager_name': 'manager_name',
                    'manager_id': 23,
                    'manager_image': 'image_url..',
                    'manager_designation': 'designation',
                    'role': 1,
                },..
            ]


        """
        users_qs = account_filter(request)

        user_list = get_user_list(users_qs)
        return Response(user_list, status=200)


class ResourceViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk, format=None):
        viewer = request.user
        user_qs = User.objects.select_related(
            'parent', 'userstate',
        ).filter(id=pk)
        if len(user_qs) < 1:
            resp = {'detail': "User not found."}
            return Response(resp, status=400)
        user = user_qs[0]
        check_same_org(user, viewer)
        user_details = get_resource_details(user)
        # print(user)
        return Response(user_details, status=200)

    def list(self, request, format=None):
        """
        Query parameters:
        ---
            status:
                type: str
                required: Yes
                choices: 'online', 'offline', 'working', 'free', 'unreachable', 'inactive','active'

        Sample Response:
        ---

            [
                {
                    'id': 37,
                    'full_name': 'Agent1',
                    'image': null,
                    'presence': true,
                    'is_unreachable': true,
                    'is_free': false,
                    'is_active': true,
                    'point': {'lat': 23.1234, 'lng': 92.323}, // null if no location found
                    'task_id': 12,
                    'task_title': 'title',
                    'event': 1,
                    'timestamp': '12-12-12 12:23:2323'
                },...
            ]


        """
        agents_qf = resource_filter(request)
        agents_qs = User.objects.select_related(
            'parent',
            'userstate__last_location',
            'userstate__active_task',
        ).filter(agents_qf)
        agent_list = get_resource_list(agents_qs)

        return Response(agent_list, status=200)


class PaginatedResources(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Query parameters:
        ---
            status:
                type: str
                required: Yes
                choices: 'online', 'offline', 'working', 'free', 'unreachable', 'inactive','active'

        Sample Response:
        ---

            [
                {
                    'id': 37,
                    'full_name': 'Agent1',
                    'image': null,
                    'presence': true,
                    'is_unreachable': true,
                    'is_free': false,
                    'is_active': true,
                    'point': {'lat': 23.1234, 'lng': 92.323}, // null if no location found
                    'task_id': 12,
                    'task_title': 'title',
                    'event': 1,
                    'timestamp': '12-12-12 12:23:2323'
                },...
            ]


        """
        agents_qf = resource_filter(request)
        agents_qs = User.objects.select_related(
            'parent',
            'userstate__last_location',
            'userstate__active_task',
        ).filter(agents_qf)

        data = get_paginated(
            agents_qs,
            request,
            get_resource_list
        )
        return Response(data, status=200)


class ProfileImageUpload(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Parameter details:
        ---
            image:
                type: image
                required: Yes

        """
        user = request.user
        url_list = get_image_urls(request, user.id, 'profile/')
        if len(url_list) > 0:
            user.image = url_list[0]
            user.save()
            user_details = get_profile_details(user)
            return Response(user_details, status=200)
        return Response({'msg': 'No image found!'}, status=406)


class FBTokenUpdateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Parameter details:
        ---
            fb_token:
                type: string
                required: Yes

        """
        user = request.user
        token = request.data.get('fb_token', False)
        if token:
            user.fb_token = token
            user.save()
            return Response({'msg': 'OK'}, status=200)
        return Response({'msg': 'No token found!'}, status=400)


class FileUpload(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Parameter details:
        ---
            file1:
                type: file
            file2:
                type: file
            .....

        Response: 200
        ---
            ['url1', 'url2', ...]
        """
        user = request.user
        url_list = get_file_urls(request, user.id, 'message/')
        if len(url_list) > 0:
            return Response(url_list, status=200)
        return Response({'msg': 'No files given!'}, status=406)


class DataUsageViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request, format=None):
        """
        Sample Submit:
        ---
            {
                'megabytes': 12.0,
            }
        """
        agent = request.user
        cur_device_mbs = request.data.get('megabytes', False)
        mac = request.data.get('mac', '')
        if not cur_device_mbs:
            return Response({'detail': 'Value not provided!'}, status=400)

        usage_qs = DataUsage.objects.filter(Q(agent=agent))
        if usage_qs.exists() > 0:
            usage = usage_qs.order_by('-timestamp')[0]
            total_mbs = usage.total_megabytes

            device_qs = usage_qs.filter(Q(mac=mac))
            if device_qs.exists():
                device_usage = device_qs.order_by('-timestamp')[0]
                last_device_mbs = device_usage.device_megabytes
                if cur_device_mbs > last_device_mbs:
                    instant_mbs = cur_device_mbs - last_device_mbs
                else:
                    instant_mbs = cur_device_mbs
            else:
                instant_mbs = cur_device_mbs
            total_mbs += instant_mbs
            # print('Old device: ' + mac + ' with total mb: ' + str(total_mbs) + ' instant md: ' + str(instant_mbs))
        else:
            total_mbs = cur_device_mbs
            instant_mbs = cur_device_mbs
            # print('New device: ' + mac + ' with total mb: ' + str(total_mbs) + ' instant md: ' + str(instant_mbs))

        usage_new = DataUsage(
            agent=agent,
            mac=mac,
            device_megabytes=cur_device_mbs,
            total_megabytes=total_mbs,
            instant_megabytes=instant_mbs
        )
        usage_new.save()
        return Response({'msg': 'OK'}, status=200)

    def retrieve(self, request, pk, format=None):
        """
        Sample response:
        ---
            {
                'megabytes': 12.0,
            }
        """
        comp_day = timezone.datetime.now() - timezone.timedelta(days=30)
        data_qs = DataUsage.objects.filter(
            Q(agent_id=pk) &
            Q(date__gt=comp_day.date())
        )
        if len(data_qs) > 0:
            usage = data_qs.aggregate(megabytes=Sum('instant_megabytes'))
            usage_data = {
                'megabytes': usage['megabytes']
            }
        else:
            usage_data = {
                'megabytes': 0.0
            }
        return Response(usage_data, status=200)

    def list(self, request, format=None):
        """
        Sample Response:
        ---
            [
                {
                    'agent_id': 201,
                    'megabytes': 12.0,
                    'agent_name': 'full_name',
                    'image': 'image_url',
                    'is_present': true,
                },..
            ]
        """
        manager = request.user
        agents = User.objects.filter(
            Q(parent=manager) &
            Q(is_active=True)
        )
        comp_day = timezone.datetime.now() - timezone.timedelta(days=30)

        usage_list = []
        for agent in agents:
            data_qs = DataUsage.objects.filter(
                Q(agent=agent) &
                Q(date__gt=comp_day.date())
            )
            if len(data_qs) > 0:
                usage = data_qs.aggregate(megabytes=Sum('instant_megabytes'))
                usage_data = {
                    'agent_id': agent.id,
                    'agent_name': agent.full_name,
                    'image': agent.image,
                    'is_present': agent.is_present,
                    'megabytes': usage['megabytes']
                }
            else:
                usage_data = {
                    'agent_id': agent.id,
                    'agent_name': agent.full_name,
                    'image': agent.image,
                    'is_present': agent.is_present,
                    'megabytes': 0.0
                }
            usage_list.append(usage_data)
        return Response(usage_list, status=200)


class DashboardManager(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):

        """
        Sample response:
        ---
            {
                'total_task': 12,
                'unassigned_task': 33,
                'delayed_task': 5,
                'remaining_task': 2,
                'complete_task': 3,
                'cancelled_task': 4,
                'inprogress_task': 5,
                'current_task': [
                    {
                        'title': 'title',
                        'status': 0,
                        'start': 'datetime',
                        'duration': 4,
                        'task_type': 'string',
                        'address': 'string',
                        'id': 2,
                    },....
                ],

                'total_agent': 100,
                'offline_agent': 3,
                'online_agent': 4,
                'working_agent': 3,
                'free_agent': 4,
                'unreachable_agent': 5,
                'is_trial': true,
                'due_days': 19,

            }
        """
        is_manager(request)
        adjust_subscription(request)
        if not check_subscription(request):
            return Response({'msg': 'Payment is due!'}, status=402)
        manager = request.user
        task_qf_manager = Q(manager=manager) | Q(agent_list=manager)
        task_qs = Task.objects.filter(task_qf_manager)
        total_task = task_qs.count()
        unassigned_task = task_qs.filter(Q(status=TSTATE['Unassigned'])).count()
        remaining_task = task_qs.filter(Q(status=TSTATE['Remaining'])).count()
        delayed_task = task_qs.filter(
            Q(delayed=True) &
            ~Q(status=TSTATE['Cancelled']) &
            ~Q(status=TSTATE['Postponed']) &
            ~Q(status=TSTATE['Complete'])
        ).count()
        complete_task = task_qs.filter(Q(status=TSTATE['Complete'])).count()
        cancelled_task = task_qs.filter(Q(status=TSTATE['Cancelled'])).count()
        inprogress_task = task_qs.filter(Q(status=TSTATE['In progress'])).count()

        current_task = get_current_task(manager)

        resource_qs = User.objects.filter(Q(parent=manager))
        total_agent = resource_qs.count()
        online_agent = resource_qs.filter(Q(is_present=True)).count()
        offline_agent = resource_qs.filter(Q(is_present=False)).count()

        working_agent = resource_qs.filter(
            Q(is_present=True) &
            Q(is_working=True) &
            Q(is_awol=False)
        ).count()
        free_agent = resource_qs.filter(
            Q(is_present=True) &
            Q(is_working=False) &
            Q(is_awol=False)
        ).count()
        unreachable_agent = resource_qs.filter(
            Q(is_present=True) &
            Q(is_awol=True)
        ).count()

        unchecked = get_unchecked_count(request)

        data = {
            'total_task': total_task,
            'unassigned_task': unassigned_task,
            'delayed_task': delayed_task,
            'remaining_task': remaining_task,
            'complete_task': complete_task,
            'cancelled_task': cancelled_task,
            'inprogress_task': inprogress_task,
            'current_task': current_task,

            'total_agent': total_agent,
            'offline_agent': offline_agent,
            'online_agent': online_agent,
            'working_agent': working_agent,
            'free_agent': free_agent,
            'unreachable_agent': unreachable_agent,
            'is_trial': manager.org.subscription._is_trial,
            'due_days': (manager.org.subscription.current_usage.exp_date - timezone.now()).days,
            'unchecked_ntf': unchecked,

        }

        return Response(data, status=200)


class DashboardAgent(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Sample Response:
        ---
            {
                'total_task': 2,
                'current_task': [
                    {
                        'title': 'title',
                        'status': 0,
                        'start': 'datetime',
                        'duration': 4,
                        'task_type': 'string',
                        'address': 'string',
                        'id': 2,
                    },....
                ],
                'delayed_task': 5,
                'remaining_task': 5,
            }

        """
        if not check_subscription(request):
            return Response({'msg': 'Payment is due!'}, status=402)
        agent = request.user
        task_qs = Task.objects.filter(Q(agent_list=agent))
        total_task = task_qs.count()
        remaining_task = task_qs.filter(Q(status=TSTATE['Remaining'])).count()
        delayed_task = task_qs.filter(
            Q(delayed=True) &
            ~Q(status=TSTATE['Cancelled']) &
            ~Q(status=TSTATE['Postponed']) &
            ~Q(status=TSTATE['Complete'])
        ).count()

        current_task = get_current_task(agent)

        unchecked = get_unchecked_count(request)

        data = {
            'total_task': total_task,
            'current_task': current_task,
            'delayed_task': delayed_task,
            'remaining_task': remaining_task,
            'unchecked_ntf': unchecked,
        }

        return Response(data, status=200)


class SearchAgentsTasks(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, token, format=None):
        """
        Query parameters:
        ---
            token:
                type: str
                required: yes

        Sample Response:
        ---
            {
                'agents':
                [
                    {'id': 116, 'name': 'Member 44', 'image': None},
                    ...
                ],
                'tasks':
                [
                    {   'id': 25,
                        'title': 'Retailer 1',
                        'status': 0,
                        'deadline': datetime.datetime(2018, 8, 14, 8, 24, 34, 913268, tzinfo=<UTC>),
                        'task_type': 'Visit2',
                        'address': 'Link road, Badda, Gulshan.',
                        'agent_list': [{'id': 114, 'image': None}]
                    },
                    ....
                ]
            }
        """
        is_manager(request)
        manager = request.user
        qcommon_task_manager = Q(manager=manager)
        qname = Q(title__icontains=token)
        qaddress = Q(address__icontains=token)
        tasks = Task.objects.select_related(
            'manager'
        ).filter(
            qcommon_task_manager &
            (qname | qaddress)
        )

        agent_qs = User.objects.select_related(
            'parent'
        ).filter(
            Q(parent=manager) &
            Q(full_name__icontains=token))

        data = {
            'agents': get_resource_list(agent_qs),
            'tasks': get_task_list(tasks)
        }

        return Response(data, status=200)


class SearchUsers(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, token, format=None):
        """
        Query parameters:
        ---
            token:
                type: str
                required: yes

        Sample Response:
        ---
            [
                {
                    'id': 116,
                    'username': 'username1',
                    'full_name': 'Member 44',
                },
                ...
            ],
        """

        user_qs = User.objects.filter(
            Q(org=request.user.org) &
            Q(role__in=[ROLE_DICT['Manager'], ROLE_DICT['Employee']]) & (
                Q(username__icontains=token) |
                Q(full_name__icontains=token)
            )
        ).distinct()[0:10]

        data = []

        for user in user_qs:
            data.append(
                {
                    'id': user.id,
                    'username': get_username(user),
                    'full_name': user.full_name,
                }
            )

        return Response(data, status=200)


