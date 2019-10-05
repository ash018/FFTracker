from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .helpers import *
from .generators import task_report_full, attendance_report_full
from apps.task.helpers import get_task_list
from apps.user.management.commands.generate_attendance_report import get_work_hours
from apps.task.config import TASK_STATUS_DICT as TSD


class TaskCombined(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Parameter details:
        ---
            manager:
                type: int
                required: Yes

            date_range:
                type: int
                default: 1
                options:
                    (1, last day),
                    (2, this week),
                    (3, last week),
                    (4, this month),
                    (5, last month),

            date:
                type: iso date
                required: No

        Sample Response:
         ---
            {
                'complete': 10,
                'delayed': 13,
                'cancelled': 14,
                'postponed': 14,
            }

        """
        task_qs = get_task_qs(request)
        complete = task_qs.filter(status=TSD['Complete']).count()
        cancelled = task_qs.filter(status=TSD['Cancelled']).count()
        delayed = task_qs.filter(delayed=True).count()
        postponed = task_qs.filter(status=TSD['Postponed']).count()

        data = {
            'complete': complete,
            'delayed': delayed,
            'cancelled': cancelled,
            'postponed': postponed
        }
        return Response(data, status=200)


class TaskFilteredList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Parameter details:
        ---
            manager:
                type: int
                required: Yes

            agent:
                type: int
                required: No

            date_range:
                type: int
                default: 1
                options:
                    (1, last day),
                    (2, this week),
                    (3, last week),
                    (4, this month),
                    (5, last month),

            date:
                type: iso date
                required: No

            status:
                type: int
                required: No
                choices:
                    (3, 'Complete'),
                    (4, 'Cancelled'),
                    (5, 'Postponed'),

            delayed:
                type: bool
                required: no

        Sample Response:
         ---
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


        """
        task_qs = get_task_qs(request)
        data = get_task_list(task_qs)
        return Response(data, status=200)


class AttendanceCombined(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Parameter details:
        ---
            manager:
                type: int
                required: Yes

            date:
                type: date str
                default: Yes

        Sample Response:
         ---
            {
                'present': 14,
                'absent': 2,
                'low_work_hour': 6,
                'low_task_hour': 23

            }

        """

        atc_qs, manager_qf, field = get_atc_qs(request)

        present = 0
        absent = 0
        low_work_hour = 0
        low_task_hour = 0

        for atc_obj in atc_qs:
            present += atc_obj.present.filter(manager_qf).count()
            absent += atc_obj.absent.filter(manager_qf).count()
            low_work_hour += atc_obj.low_work_hour.filter(manager_qf).count()
            low_task_hour += atc_obj.low_task_hour.filter(manager_qf).count()

        data = {
            'present': present,
            'absent': absent,
            'low_work_hour': low_work_hour,
            'low_task_hour': low_task_hour
        }

        return Response(data, status=200)


class AttendanceFiltered(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Parameter details:
        ---
            manager:
                type: int
                required: Yes

            date:
                type: date str
                required: Yes

            field:
                type: str
                choices: 'present', 'absent', 'low_work_hour', 'low_task_hour', 'late_arrival'

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

        atc_qs, manager_qf, field = get_atc_qs(request)
        data = []

        for atc_obj in atc_qs:
            users = []
            if field == 'present':
                users = atc_obj.present.filter(manager_qf)
            if field == 'absent':
                users = atc_obj.absent.filter(manager_qf)
            if field == 'low_work_hour':
                users = atc_obj.low_work_hour.filter(manager_qf)
            if field == 'low_task_hour':
                users = atc_obj.low_task_hour.filter(manager_qf)
            if field == 'late_arrival':
                users = atc_obj.late_arrival.filter(manager_qf)

            att_list = get_attendance_list(users, atc_obj.date)
            for att in att_list:
                data.append(att)

        return Response(data, status=200)


class AttendanceIndividual(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Parameter details:
        ---

            agent:
                type: int
                required: Yes

            date:
                type: date str
                required: Yes

            date_range:
                type: int
                Choices: (1, last day), (2, last week), (3, last month)
                Default: 1

        Sample Response:
         ---
            {
                'present': 14,
                'absent': 2,
                'low_work_hour': 6,
                'low_task_hour': 23

            }
        """
        org = request.user.org
        ati_qs = get_ati_qs(request)

        min_work_hour = get_work_hours(org) * (org.min_work_hour_p / 100)
        present_qs = ati_qs.filter(Q(status=ASD['Present']))

        present = present_qs.count()
        absent = ati_qs.filter(Q(status=ASD['Absent'])).count()
        low_work_hour = present_qs.filter(Q(work_hour__lt=min_work_hour)).count()
        low_task_hour = present_qs.filter(Q(task_hour_p__lt=org.min_task_hour_p)).count()

        data = {
            'present': present,
            'absent': absent,
            'low_work_hour': low_work_hour,
            'low_task_hour': low_task_hour
        }

        return Response(data, status=200)


class Rankings(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Parameter details:
        ---
            topic:
                type: str
                required: Yes
                choices:
                    'absence',
                    'low_task_hour',
                    'low_work_hour',
                    'overtime',
                    'late_arrival',
                    'delayed_task',
                    'travel_distance'

            manager:
                type: int
                required: Yes

            date_range:
                type: int
                default: 1
                options:
                    (2, this week),
                    (3, last week),
                    (4, this month),
                    (5, last month),


        Sample Response:
         ---
            [
                {
                    'topic': <topic>,
                    'id': 12,
                    'agent_name': 'agent1',
                    'image': 'url1',
                    <topic>: 10, // topic comes from the choice list
                },...
            ]


        """
        top_five, topic = get_ranking_qs(request)
        data = get_ranking_details(top_five, topic)

        return Response(data, status=200)


class AttendanceExport(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Parameter details:
        ---
            agent:
                type: int
                default: False

            manager:
                type: int
                default: False

            date_range:
                type: int
                default: 1
                options: (1, last day), (2, last week), (3, last month)

            date:
                type: date str
                default: false

        Sample Response:
         ---
            [
                {
                    'date': date_string,
                    'agent': 'full_name',
                    'team': 'team_name',
                    'status': 'Present',
                    'entry_time': timestamp,
                    'exit_time': timestamp,
                    'work_hour': '02:30:49'
                },

                {
                    'date': date_string,
                    'agent': 'full_name',
                    'team': 'team_name',
                    'status': 'Present',
                    'entry_time': timestamp,
                    'exit_time': timestamp,
                    'work_hour': '02:30:49'
                },....

            ]

        """
        date_wise_counts = attendance_report_full(request)

        return Response(date_wise_counts, status=200)


class TaskExport(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Parameter details:
        ---
            agent:
                type: int
                default: False
            date_range:
                type: int
                default: 1
                options: (1, last day), (2, last week), (3, last month)

            date:
                type: date str
                default: false

        Sample Response:
         ---
            [
                {
                    'deadline': timestamp,
                    'title': 'task.title',
                    'agent': 'full_name',
                    'expected_duration': '02:30:49',
                    'actual_duration': 02:30:49',
                    'address': 'task address',
                    'status': 'task status',
                    'delayed': 'Yes'/'No'
                },

                {
                    'deadline': timestamp,
                    'title': 'task.title',
                    'agent': 'full_name',
                    'expected_duration': '02:30:49',
                    'actual_duration': 02:30:49',
                    'address': 'task address',
                    'status': 'task status',
                    'delayed': 'Yes'/'No'
                },....

            ]

        """
        data = task_report_full(request)
        return Response(data, status=200)
