import pytz
import json
# from django.db.models import Q
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from apps.user.helpers import create_agent, create_manager, create_organizer
from apps.user.auth_helpers import get_username
from apps.report.urls import REPORT_URLS
from apps.report.helpers import create_attendance
from apps.report.config import RANGE_DICT
from apps.task.models import Task
from apps.task.config import TASK_STATUS_DICT as TSD
# from .models import AttendanceCombined as ATC, \
#     AttendanceIndividual as ATI, Ranking
# from .config import ATTENDANCE_STATUS_DICT as ASD

from apps.user.management.commands.generate_attendance_report import generate_atc_daily
from apps.user.management.commands.generate_ranking import generate_ranking_daily


User = get_user_model()
client = APIClient()
location_prefix = '/v0/location/'
user_prefix = '/v0/user/'
report_prefix = '/v0/report/'
utc = pytz.UTC


def create_task_rpt(
        manager,
        agent_list=[],
        deadline=timezone.now(),
        status=TSD['Unassigned'],
        delayed=False):
    task = Task.objects.create(
        title='Title',
        task_type='Visit',
        date=deadline.date(),
        start=deadline,
        deadline=deadline + timezone.timedelta(hours=4),
        delayed=delayed,
        manager=manager,
        status=status,
        org=manager.org,
    )
    if len(agent_list) > 0 and status == TSD['Unassigned']:
        task.status = TSD['Remaining']
    for agent in agent_list:
        agent.is_present = True
        if status == TSD['In progress']:
            agent.userstate.active_task_id = task.id
        agent.save()
        task.agent_list.add(agent)
    task.save()
    return task


def find_user(dict_list, username):
    for x in dict_list:
        if x['username'] == username:
            return x
    else:
        return None


def combined_attendance_check(inst, manager, range_int, topics, counts):
    client.force_authenticate(manager)
    response = client.get(
        report_prefix + REPORT_URLS['attendance_combined'],
        {
            'date': str(inst.date.date()),
            'date_range': range_int,
            'manager': manager.id,
        },
        format='json',
    )
    inst.assertEqual(response.status_code, 200)
    # print(response.data)
    for topic, count in zip(topics, counts):
        inst.assertEqual(response.data[topic], count)


def attendance_filtered_check(inst, range_int, state, count):
    response = client.get(
        report_prefix + REPORT_URLS['attendance_filtered'],
        {
            'date': str(inst.date.date()),
            'manager': inst.manager1.id,
            'date_range': range_int,
            'field': state,
        },
        format='json',
    )

    # print(json.dumps(response.data))

    inst.assertEqual(response.status_code, 200)
    inst.assertEqual(len(response.data), count)


def common_individual_check(inst, agent, range_int, state, count):
    response = client.get(
        report_prefix + REPORT_URLS['attendance_individual'],
        {
            'agent': agent.id,
            'date': str(inst.date.date()),
            'date_range': range_int,
        },
        format='json',
    )
    # print(response.data)
    inst.assertEqual(response.status_code, 200)
    inst.assertEqual(response.data[state], count)


def common_ranking_check(inst, agent, range_int, topic, count):
    response = client.get(
        report_prefix + REPORT_URLS['rankings'],
        {
            'manager': inst.manager1.id,
            'date_range': range_int,
            'date': str(inst.date.date()),
            'topic': topic
        },
        format='json',
    )

    # print(response.data)
    inst.assertEqual(response.status_code, 200)
    inst.assertEqual(
        find_user(
            response.data, get_username(agent)
        )[topic],
        count
    )


def create_attendances(inst):
    generate_atc_daily(inst.organizer1.org, inst.date)
    for i in range(1, 9):
        date = inst.date - timezone.timedelta(days=i)
        # print(str(date))
        generate_atc_daily(inst.organizer1.org, date)


class ReportTestCase(TestCase):

    def setUp(self):
        self.username1 = 'username1'
        self.username2 = 'username2'
        self.username3 = 'username3'
        self.username4 = 'username4'
        self.username5 = 'username5'
        self.username6 = 'username6'
        self.username7 = 'username7'
        self.username8 = 'username8'
        self.username9 = 'username9'
        self.username10 = 'username10'

        self.username11 = 'username11'
        self.username12 = 'username12'

        self.organizer1 = create_organizer(self.username11, 'org1')
        self.organizer2 = create_organizer(self.username12, 'org2')

        self.manager1 = create_manager(self.username1, self.organizer1, self.organizer1.org)

        self.agent11 = create_agent(self.username2, self.manager1, is_present=False)
        self.agent12 = create_agent(self.username3, self.manager1, is_present=False)
        self.agent13 = create_agent(self.username4, self.manager1, is_present=False)
        self.agent14 = create_agent(self.username8, self.manager1, is_present=False)

        self.manager2 = create_manager(self.username5, self.organizer1, self.organizer1.org)
        self.agent21 = create_agent(self.username6, self.manager2, is_present=False)
        self.agent22 = create_agent(self.username7, self.manager2, is_present=False)
        self.agent23 = create_agent(self.username9, self.manager2, is_present=False)

        date_str = '2019-03-06'

        # Feb 2019: 26/tue, 27/wed, 28/thu. Mar 2019: 1/fri, 2/sat, 3/sun, 4/mon, 5/tue, 6/wed
        date = timezone.datetime.strptime(date_str, '%Y-%m-%d')
        date = utc.localize(date)
        date += timezone.timedelta(hours=9)
        self.date = date

        # Creating attendance current day.................................
        date_6_3_19 = date
        create_attendance(
            self.agent11, task_hour_p=49.0,
            date=date_6_3_19
        )
        create_attendance(
            self.agent12,
            work_hour=timezone.timedelta(hours=6),
            date=date_6_3_19
        )
        create_attendance(
            self.agent13,
            date=date_6_3_19
        )

        create_attendance(
            self.agent21, late_arrival=True,
            date=date_6_3_19
        )
        create_attendance(
            self.agent22,
            work_hour=timezone.timedelta(hours=6),
            date=date_6_3_19
        )
        # This week/month for agent11..........................
        date_5_3_19 = date - timezone.timedelta(days=1)

        create_attendance(
            self.agent11,
            date=date_5_3_19
        )
        create_attendance(
            self.agent12,
            work_hour=timezone.timedelta(hours=6),
            date=date_5_3_19
        )

        create_attendance(
            self.agent13,
            date=date_5_3_19
        )

        create_attendance(
            self.agent14,
            date=date_5_3_19
        )

        date_4_3_19 = date - timezone.timedelta(days=2)

        create_attendance(
            self.agent11, late_arrival=True,
            date=date_4_3_19
        )

        create_attendance(
            self.agent12,
            date=date_4_3_19
        )

        create_attendance(
            self.agent14,
            date=date_4_3_19
        )

        date_3_3_19 = date - timezone.timedelta(days=3)

        create_attendance(
            self.agent11, task_hour_p=49.0,
            date=date_3_3_19
        )

        create_attendance(
            self.agent12, task_hour_p=49.0,
            date=date_3_3_19
        )

        create_attendance(
            self.agent13,
            date=date_3_3_19
        )

        # last week/month for agent11...........

        date_28_2_19 = date - timezone.timedelta(days=6)

        create_attendance(
            self.agent11, task_hour_p=49.0,
            date=date_28_2_19
        )

        create_attendance(
            self.agent12,
            work_hour=timezone.timedelta(hours=6),
            date=date_28_2_19
        )

        create_attendance(
            self.agent14,
            date=date_28_2_19
        )

        date_27_2_19 = date - timezone.timedelta(days=7)

        create_attendance(
            self.agent11,
            work_hour=timezone.timedelta(hours=6),
            date=date_27_2_19
        )

        create_attendance(
            self.agent12, task_hour_p=49.0,
            date=date_27_2_19
        )

        create_attendance(
            self.agent13,
            date=date_27_2_19
        )

        date_26_2_19 = date - timezone.timedelta(days=8)

        create_attendance(
            self.agent11, task_hour_p=49.0,
            date=date_26_2_19
        )

        create_attendance(
            self.agent12,
            date=date_26_2_19
        )

        create_attendance(
            self.agent13,
            work_hour=timezone.timedelta(hours=6),
            date=date_26_2_19
        )

        create_attendance(
            self.agent14,
            date=date_26_2_19
        )

        # Creating tasks this week/month.................................
        create_task_rpt(
            self.manager1, [self.agent11],
            deadline=date-timezone.timedelta(days=1),
            status=TSD['Complete']
        )
        create_task_rpt(
            self.manager1, [self.agent11],
            deadline=date-timezone.timedelta(days=1),
            status=TSD['Cancelled']
        )
        create_task_rpt(
            self.manager1, [self.agent13],
            deadline=date-timezone.timedelta(days=2),
            status=TSD['Remaining'],
            delayed=True
        )
        create_task_rpt(
            self.manager1, [self.agent12],
            deadline=date-timezone.timedelta(days=2),
            status=TSD['Postponed']
        )

        create_task_rpt(
            self.manager1, [self.agent13],
            deadline=date-timezone.timedelta(days=3),
            status=TSD['Remaining'],
            delayed=True
        )

        create_task_rpt(
            self.manager1, [self.agent12],
            deadline=date-timezone.timedelta(days=3),
            status=TSD['Complete'],
            delayed=True
        )

        # last week/month...........

        create_task_rpt(
            self.manager1, [self.agent11],
            deadline=date-timezone.timedelta(days=6),
            status=TSD['Complete']
        )
        create_task_rpt(
            self.manager1, [self.agent11],
            deadline=date-timezone.timedelta(days=6),
            status=TSD['Cancelled']
        )
        create_task_rpt(
            self.manager1, [self.agent13],
            deadline=date-timezone.timedelta(days=7),
            status=TSD['Remaining'],
            delayed=True
        )
        create_task_rpt(
            self.manager1, [self.agent12],
            deadline=date-timezone.timedelta(days=7),
            status=TSD['Postponed']
        )

        create_task_rpt(
            self.manager1, [self.agent13],
            deadline=date-timezone.timedelta(days=8),
            status=TSD['Remaining'],
            delayed=True
        )

        create_task_rpt(
            self.manager1, [self.agent12],
            deadline=date-timezone.timedelta(days=8),
            status=TSD['Complete'],
            delayed=True
        )

        # generate_atc_daily(self.organizer1.org, date)
        # generate_atc_daily(self.organizer1.org, date)

    def test_attendance_combined_report(self):
        create_attendances(self)
        topics = ['present', 'absent', 'low_work_hour', 'low_task_hour']

        counts = [3, 1, 1, 1]
        combined_attendance_check(
            self, self.manager1,
            RANGE_DICT['last_day'],
            topics, counts
        )

        counts = [13, 3, 2, 3]
        combined_attendance_check(
            self, self.manager1,
            RANGE_DICT['this_week'],
            topics, counts
        )

        counts = [13, 3, 2, 3]
        combined_attendance_check(
            self, self.manager1,
            RANGE_DICT['this_month'],
            topics, counts
        )

        counts = [10, 2, 3, 3]
        combined_attendance_check(
            self, self.manager1,
            RANGE_DICT['last_week'],
            topics, counts
        )

        counts = [10, 2, 3, 3]
        combined_attendance_check(
            self, self.manager1,
            RANGE_DICT['last_month'],
            topics, counts
        )

    def test_attendance_filter_report(self):
        create_attendances(self)

        client.force_authenticate(self.manager1)

        attendance_filtered_check(self, RANGE_DICT['last_day'], 'present', 3)
        attendance_filtered_check(self, RANGE_DICT['this_week'], 'present', 13)
        attendance_filtered_check(self, RANGE_DICT['last_week'], 'present', 10)

        attendance_filtered_check(self, RANGE_DICT['last_day'], 'absent', 1)
        attendance_filtered_check(self, RANGE_DICT['this_week'], 'absent', 3)
        attendance_filtered_check(self, RANGE_DICT['last_week'], 'absent', 2)

        attendance_filtered_check(self, RANGE_DICT['last_day'], 'low_work_hour', 1)
        attendance_filtered_check(self, RANGE_DICT['this_week'], 'low_work_hour', 2)
        attendance_filtered_check(self, RANGE_DICT['last_week'], 'low_work_hour', 3)

        attendance_filtered_check(self, RANGE_DICT['last_day'], 'low_task_hour', 1)
        attendance_filtered_check(self, RANGE_DICT['this_week'], 'low_task_hour', 3)
        attendance_filtered_check(self, RANGE_DICT['last_week'], 'low_task_hour', 3)

        client.force_authenticate(None)
        client.force_authenticate(self.manager2)
        attendance_filtered_check(self, RANGE_DICT['last_day'], 'absent', 1)

    def test_attendance_individual_report(self):
        create_attendances(self)

        client.force_authenticate(self.manager1)

        # ati_qs = ATI.objects.filter(
        #     Q(user_id=self.agent14.id) &
        #     Q(status=ASD['Absent'])
        # )
        # for ati in ati_qs:
        #     print(ati.user.username + '-> ' + str(ati.date))

        common_individual_check(self, self.agent11, RANGE_DICT['this_week'], 'present', 4)
        common_individual_check(self, self.agent14, RANGE_DICT['this_week'], 'absent', 2)
        common_individual_check(self, self.agent12, RANGE_DICT['this_week'], 'low_work_hour', 2)
        common_individual_check(self, self.agent11, RANGE_DICT['this_week'], 'low_task_hour', 2)

        common_individual_check(self, self.agent11, RANGE_DICT['last_week'], 'present', 3)
        common_individual_check(self, self.agent14, RANGE_DICT['last_week'], 'absent', 1)
        common_individual_check(self, self.agent12, RANGE_DICT['last_week'], 'low_work_hour', 1)
        common_individual_check(self, self.agent11, RANGE_DICT['last_week'], 'low_task_hour', 2)

    def test_attendance_individual_report_fail(self):
        create_attendances(self)

        client.force_authenticate(self.manager1)
        response = client.get(
            report_prefix + REPORT_URLS['attendance_individual'],
            {
                'date_range': 2,
                'date': str(self.date.date()),
            },
            format='json',
        )

        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_task_combined_report(self):
        client.force_authenticate(self.manager1)
        response = client.get(
            report_prefix + REPORT_URLS['task_combined'],
            {
                'manager': self.manager1.id,
                'date': self.date.date(),
                'date_range': RANGE_DICT['last_week'],
            },
            format='json',
        )

        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['complete'], 2)
        self.assertEqual(response.data['cancelled'], 1)
        self.assertEqual(response.data['postponed'], 1)
        self.assertEqual(response.data['delayed'], 3)

        client.force_authenticate(None)
        client.force_authenticate(self.agent11)
        response = client.get(
            report_prefix + REPORT_URLS['task_combined'],
            {
                'agent': self.agent12.id,
                'date': self.date.date(),
                'date_range': RANGE_DICT['last_week'],
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['complete'], 1)
        self.assertEqual(response.data['cancelled'], 0)
        self.assertEqual(response.data['postponed'], 1)
        self.assertEqual(response.data['delayed'], 1)

    def test_task_filtered_report(self):
        client.force_authenticate(self.manager1)
        response = client.get(
            report_prefix + REPORT_URLS['task_filtered'],
            {
                'manager': self.manager1.id,
                'date_range': RANGE_DICT['this_week'],
                'date': self.date.date(),
                'status': TSD['Cancelled']
            },
            format='json',
        )

        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = client.get(
            report_prefix + REPORT_URLS['task_filtered'],
            {
                'manager': self.manager1.id,
                'date_range': RANGE_DICT['last_week'],
                'date': self.date.date(),
                'status': TSD['Cancelled']
            },
            format='json',
        )

        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_ranking(self):
        create_attendances(self)

        generate_ranking_daily(self.organizer1.org, self.date)

        client.force_authenticate(self.manager1)
        common_ranking_check(self, self.agent14, RANGE_DICT['this_week'], 'absence', 2)
        common_ranking_check(self, self.agent13, RANGE_DICT['this_week'], 'delayed_task', 2)
        common_ranking_check(self, self.agent12, RANGE_DICT['this_week'], 'low_work_hour', 2)
        common_ranking_check(self, self.agent11, RANGE_DICT['this_week'], 'low_task_hour', 2)

        common_ranking_check(self, self.agent14, RANGE_DICT['last_week'], 'absence', 1)
        common_ranking_check(self, self.agent13, RANGE_DICT['last_week'], 'delayed_task', 2)
        common_ranking_check(self, self.agent12, RANGE_DICT['last_week'], 'low_work_hour', 1)
        common_ranking_check(self, self.agent11, RANGE_DICT['last_week'], 'low_task_hour', 2)

        common_ranking_check(self, self.agent14, RANGE_DICT['this_month'], 'absence', 2)
        common_ranking_check(self, self.agent13, RANGE_DICT['this_month'], 'delayed_task', 2)
        common_ranking_check(self, self.agent12, RANGE_DICT['this_month'], 'low_work_hour', 2)
        common_ranking_check(self, self.agent11, RANGE_DICT['this_month'], 'low_task_hour', 2)

        common_ranking_check(self, self.agent14, RANGE_DICT['last_month'], 'absence', 1)
        common_ranking_check(self, self.agent13, RANGE_DICT['last_month'], 'delayed_task', 2)
        common_ranking_check(self, self.agent12, RANGE_DICT['last_month'], 'low_work_hour', 1)
        common_ranking_check(self, self.agent11, RANGE_DICT['last_month'], 'low_task_hour', 2)

    def test_attendance_export(self):
        client.force_authenticate(self.manager1)
        response = client.get(
            report_prefix + REPORT_URLS['attendance_export'],
            {
                'manager': self.manager1.id,
                'date_range': RANGE_DICT['this_week'],
                'date': str(self.date.date()),
            },
            format='json',
        )

        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data),
            13
        )

        response = client.get(
            report_prefix + REPORT_URLS['attendance_export'],
            {
                'manager': self.manager1.id,
                'date_range': RANGE_DICT['last_week'],
                'date': str(self.date.date()),
            },
            format='json',
        )

        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data),
            10
        )

    def test_task_export(self):
        client.force_authenticate(self.manager1)
        response = client.get(
            report_prefix + REPORT_URLS['task_export'],
            {
                'manager': self.manager1.id,
                'date_range': RANGE_DICT['this_week'],
                'date': str(self.date.date()),
            },
            format='json',
        )

        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data),
            6
        )

