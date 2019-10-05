from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.common.task_templates import *
from apps.task.config import TASK_STATUS_DICT as TSTATE
from apps.task.helpers import create_task
from apps.task.models import Task, TaskTemplate
from apps.task.urls import TASK_URLS
from apps.user.helpers import create_agent, create_manager, create_organizer

User = get_user_model()
client = APIClient()
task_prefix = '/v0/task/'
user_prefix = '/v0/user/'


def set_duration(hours=2):
    return timezone.now() + timezone.timedelta(hours=hours)


def create_task_template(task_type, task_fields, manager):
    task_template = TaskTemplate.objects.create(
        task_type=task_type,
        task_fields=task_fields,
    )
    task_template.org_id = manager.org_id
    task_template.user_id = manager.id
    task_template.save()
    return task_template


def test_task_complete(self):
    client.force_authenticate(self.manager1)
    response = client.post(
        task_prefix + TASK_URLS['create_task_manager'],
        {
            'title': 'Task1',
            'manager': self.manager1.id,
            'task_type': 'Retailer Visit',
            'start': "2018-07-31T05:07:24+00:00",
            "deadline": "2018-07-31T07:07:24+00:00",
            'agent_list': [self.agent12.id, self.agent11.id],
            # 'point': {'lat': 23.780926, 'lng': 90.422858},
        },
        format='json',
    )
    # print(response.data)
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    task = Task.objects.filter(
        Q(manager=self.manager1) &
        Q(status=TSTATE['Remaining'])
    )[0]
    self.assertEqual(task.title, 'Task1')

    client.force_authenticate(None)
    client.force_authenticate(self.agent11)

    response = client.patch(
        task_prefix + TASK_URLS['change_task_state_agent'].replace('<int:pk>', str(task.id)),
        {
            'status': TSTATE['In progress'],
            'custom_fields': {},
            'event_point': {'lat': 23.780926, 'lng': 90.422858}
        },
        format='json',
    )
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.agent11.refresh_from_db()
    self.agent12.refresh_from_db()
    self.assertEqual(self.agent11.is_working, True)
    self.assertEqual(self.agent12.is_working, True)

    response = client.patch(
        task_prefix + TASK_URLS['change_task_state_agent'].replace('<int:pk>', str(task.id)),
        {
            'status': TSTATE['Complete'],
            'custom_fields': {},
            'event_point': {'lat': 23.780926, 'lng': 90.422858}
        },
        format='json',
    )
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.agent11.refresh_from_db()
    self.agent12.refresh_from_db()
    self.assertEqual(self.agent11.is_working, False)
    self.assertEqual(self.agent12.is_working, False)


class TaskTestCase(TestCase):

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

        self.agent11 = create_agent(self.username2, self.manager1)
        self.agent12 = create_agent(self.username3, self.manager1)
        self.agent13 = create_agent(self.username4, self.manager1)
        self.agent14 = create_agent(self.username8, self.manager1)

        self.manager2 = create_manager(self.username5, self.organizer1, self.organizer1.org)
        self.agent21 = create_agent(self.username6, self.manager2)
        self.agent22 = create_agent(self.username7, self.manager2)

    def test_create_task_success(self):
        client.force_authenticate(self.manager1)
        response = client.post(
            task_prefix + TASK_URLS['create_task_manager'],
            {
                'title': 'Task1',
                'manager': self.manager1.id,
                'task_type': 'Retailer Visit',
                'start': "2018-07-31T05:07:24+00:00",
                "deadline": "2018-07-31T07:07:24+00:00",
                'agent_list': [self.agent12.id, self.agent11.id],
                # 'point': {'lat': 23.780926, 'lng': 90.422858},
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = list(Task.objects.filter(manager=self.manager1))[0]
        self.assertEqual(task.title, 'Task1')

        response = client.post(
            task_prefix + TASK_URLS['create_task_manager'],
            {
                "title": "My First Task",
                'manager': self.manager1.id,
                "start": "2018-07-31T05:07:24+00:00",
                "deadline": "2018-07-31T07:07:24+00:00",
                "images": ['url1..', 'url2..'],
                "image_required": True,
                "attachment_required": True,
                "task_type": "Installation",
                "agent_list": [self.agent12.id, self.agent11.id],
                "point": {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        # print(response.data)
        # agent12 = User.objects.get(id=self.agent12.id)
        # for ts in agent12.timeslots.all():
        #     print(ts.id)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_task_agent_success(self):
        client.force_authenticate(self.agent13)
        response = client.post(
            task_prefix + TASK_URLS['create_task_agent'],
            {
                'title': 'Task1',
                'manager': self.agent13.parent.id,
                'agent_list': [self.agent13.id],
                'task_type': 'Retailer Visit',
                "images": ['url1..', 'url2..'],
                'start': "2018-07-31T05:07:24+00:00",
                "deadline": "2018-07-31T07:07:24+00:00",
                # 'point': {'lat': 23.780926, 'lng': 90.422858},
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = client.post(
            task_prefix + TASK_URLS['create_task_agent'],
            {
                "title": "My First Task",
                'manager': self.agent13.parent.id,
                'agent_list': [self.agent13.id],
                "start": "2018-07-31T05:07:24+00:00",
                "deadline": "2018-07-31T07:07:24+00:00",
                "images": ['url1..', 'url2..'],
                "image_required": True,
                "attachment_required": True,
                "task_type": "Installation",
                "point": {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = client.get(
            task_prefix + TASK_URLS['get_task_list_agent'],
            {
                'status': TSTATE['Remaining']
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], 'Task1')

    def test_create_task_multiple_success_manager(self):
        client.force_authenticate(self.manager1)
        response = client.post(
            task_prefix + TASK_URLS['create_task_manager'],
            {
                'title': 'Task_4',
                'manager': self.manager1.id,
                'instances': 4,
                'task_type': 'Retailer Visit',
                'start': "2018-07-31T05:07:24+00:00",
                "deadline": "2018-07-31T07:07:24+00:00",
                "images": ['url1..', 'url2..'],
                'agent_list': [self.agent12.id, self.agent11.id],
                # 'point': {'lat': 23.780926, 'lng': 90.422858},
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = list(Task.objects.filter(manager=self.manager1))[0]
        self.assertEqual(task.title, 'Task_4')

        response = client.get(
            task_prefix + TASK_URLS['get_task_list_manager'],
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_task_success(self):
        task = create_task('Task2', self.manager1, [self.agent13])

        client.force_authenticate(self.manager1)
        response = client.get(
            task_prefix + TASK_URLS['get_task_manager'].replace('<int:pk>', str(task.id)),
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], task.title)

        client.force_authenticate(user=None)
        client.force_authenticate(self.agent13)
        response = client.get(
            task_prefix + TASK_URLS['get_task_agent'].replace('<int:pk>', str(task.id)),
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], task.title)

    def test_get_task_fail(self):
        task = create_task('Task2', self.manager1, [self.agent13])

        client.force_authenticate(user=None)
        client.force_authenticate(self.agent12)
        response = client.get(
            task_prefix + TASK_URLS['get_task_agent'].replace('<int:pk>', str(task.id)),
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_address(self):
        client.force_authenticate(self.manager1)
        response = client.post(
            task_prefix + TASK_URLS['get_address_from_point'],
            {
                'point': {'lat': 23.780926, 'lng': 90.422858},
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_task_success(self):
        client.force_authenticate(self.manager1)
        task = create_task('Task2', self.manager1, [self.agent13])

        response = client.patch(
            task_prefix + TASK_URLS['edit_task_manager'].replace('<int:pk>', str(task.id)),
            {
                "title": "My First Task",
                'manager': self.manager1.id,
                "start": "2018-07-31T05:07:24+00:00",
                "deadline": "2018-07-31T07:07:24+00:00",
                "images": ['url1..', 'url2..'],
                "image_required": True,
                "attachment_required": True,
                "task_type": "Installation",
                "agent_list": [self.agent12.id, self.agent11.id],
                # "point": {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_task_fail(self):
        client.force_authenticate(self.manager1)
        task = create_task('Task2', self.manager1, [self.agent13], status=TSTATE['In progress'])

        response = client.patch(
            task_prefix + TASK_URLS['edit_task_manager'].replace('<int:pk>', str(task.id)),
            {
                "title": "My First Task",
                'manager': self.manager1.id,
                "start": "2018-07-31T05:07:24+00:00",
                "deadline": "2018-07-31T07:07:24+00:00",
                "images": ['url1..', 'url2..'],
                "image_required": True,
                "attachment_required": True,
                "task_type": "Installation",
                "agent_list": [self.agent12.id, self.agent11.id],
                # "point": {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    # def test_edit_task_permission(self):
    #     task = create_task('Task2', self.manager1, [self.agent13])
    #
    #     client.force_authenticate(self.manager2)
    #     response = client.patch(
    #         task_prefix + TASK_URLS['edit_task_manager'].replace('<int:pk>', str(task.id)),
    #         {
    #             "title": "My First Task",
    #             'manager': self.manager1.id,
    #             "start": "2018-07-31T05:07:24+00:00",
    #             "deadline": "2018-07-31T07:07:24+00:00",
    #             "image_required": True,
    #             "attachment_required": True,
    #             "task_type": "Installation",
    #             "agent_list": [self.agent12.id, self.agent11.id],
    #             # "point": {'lat': 23.780926, 'lng': 90.422858}
    #         },
    #         format='json',
    #     )
    #     # print(response.data)
    #     self.assertEqual(response.status_code, 403)

    def test_get_task_list_manager(self):
        task1 = create_task('Task_test1', self.manager1, [self.agent11, self.agent12])
        task2 = create_task('Task_test2', self.manager1, [self.agent11, self.agent12], status=TSTATE['In progress'])
        task3 = create_task('Task_test3', self.manager1, [self.agent13])

        task4 = create_task('Task_test4', self.manager2, [self.agent21, self.agent22])
        task5 = create_task('Task_test5', self.manager2, [self.agent22])

        client.force_authenticate(self.manager1)
        response = client.get(
            task_prefix + TASK_URLS['get_task_list_manager'],
            {
                'status': TSTATE['In progress'],
                'agent_id': self.agent11.id
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.get(
            task_prefix + TASK_URLS['get_task_list_manager'],
            {
                'manager_id': self.manager1.id
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_task_list_organizer(self):
        task1 = create_task('Task_test1', self.manager1, [self.agent11, self.agent12])
        task2 = create_task('Task_test2', self.manager1, [self.agent11, self.agent12], status=TSTATE['In progress'])
        task3 = create_task('Task_test3', self.manager1, [self.agent13])

        task4 = create_task('Task_test4', self.manager2, [self.agent21, self.agent22])
        task5 = create_task('Task_test5', self.manager2, [self.agent22])

        client.force_authenticate(self.organizer1)

        response = client.get(
            task_prefix + TASK_URLS['get_task_list_paginated'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)

    def test_get_task_list_search(self):
        task1 = create_task('New Task 1', self.manager1, [self.agent11, self.agent12])
        task2 = create_task('New Task 2', self.manager1, [self.agent11, self.agent12])
        task3 = create_task('New Task 3', self.manager1, [self.agent13])
        task4 = create_task('New Task 4', self.manager1, [self.agent13])

        task5 = create_task('Heavy Work', self.manager1, [self.agent13, self.agent12])

        client.force_authenticate(self.manager1)
        response = client.get(
            task_prefix + TASK_URLS['get_task_list_paginated'],
            {
                'token': 'New Task',
            },
            format='json',
        )
        # print(json.dumps(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)

    def test_get_task_list_agent(self):
        task1 = create_task('Task_test1', self.manager1, [self.agent11, self.agent12])
        task2 = create_task('Task_test2', self.manager1, [self.agent11, self.agent12], status=TSTATE['In progress'])
        task3 = create_task('Task_test3', self.manager1, [self.agent13])

        client.force_authenticate(self.agent11)
        response = client.get(
            task_prefix + TASK_URLS['get_task_list_agent'],
            {
                'status': TSTATE['Remaining']
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_unassigned_task_list_agent(self):
        task1 = create_task('Task_test1', self.manager1)
        task2 = create_task('Task_test2', self.manager1)
        task3 = create_task('Task_test3', self.manager1, [self.agent13])

        client.force_authenticate(self.agent13)
        response = client.get(
            task_prefix + TASK_URLS['get_task_list_agent'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        response = client.get(
            task_prefix + TASK_URLS['get_task_list_agent'],
            {
                'status': 0,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_self_assign_task_agent(self):
        task1 = create_task('Task_test1', self.manager1)
        task2 = create_task('Task_test2', self.manager1)
        task3 = create_task('Task_test3', self.manager1, [self.agent13])

        client.force_authenticate(self.agent11)
        response = client.post(
            task_prefix + TASK_URLS['assign_task_agent'].replace('<int:pk>', str(task1.id)),
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_task_state_manager_success(self):
        task1 = create_task('Task_test1', self.manager1, [self.agent11, self.agent12])

        client.force_authenticate(self.manager1)
        response = client.post(
            task_prefix + TASK_URLS['change_task_state_manager'].replace('<int:pk>', str(task1.id)),
            {
                'status': TSTATE['Cancelled']
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_change_task_state_manager_permission(self):
    #     task1 = create_task('Task_test1', self.manager1, [self.agent11, self.agent12])
    #
    #     client.force_authenticate(user=None)
    #     client.force_authenticate(self.manager2)
    #     response = client.post(
    #         task_prefix + TASK_URLS['change_task_state_manager'].replace('<int:pk>', str(task1.id)),
    #         {
    #             'status': TSTATE['Cancelled']
    #         },
    #         format='json',
    #     )
    #     self.assertEqual(response.status_code, 403)

    def test_change_task_state_manager_fail(self):
        task1 = create_task('Task_test_status', self.manager1, [self.agent11, self.agent12])
        # manager can't start task
        client.force_authenticate(self.manager1)
        response = client.post(
            task_prefix + TASK_URLS['change_task_state_manager'].replace('<int:pk>', str(task1.id)),
            {
                'status': TSTATE['In progress']
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        client.force_authenticate(user=None)
        client.force_authenticate(self.agent11)
        response = client.patch(
            task_prefix + TASK_URLS['change_task_state_agent'].replace('<int:pk>', str(task1.id)),
            {
                'status': TSTATE['In progress'],
                'custom_fields': {},
                'event_point': {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        client.force_authenticate(user=None)
        client.force_authenticate(self.manager1)
        # manager can't change in progress task
        response = client.post(
            task_prefix + TASK_URLS['change_task_state_manager'].replace('<int:pk>', str(task1.id)),
            {
                'status': TSTATE['Cancelled']
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_execute_task_agent_success(self):
        task1 = create_task('Task_test1', self.manager1, [self.agent11, self.agent12])
        task2 = create_task('Task_test1', self.manager1, [self.agent11])

        client.force_authenticate(self.agent11)
        response = client.patch(
            task_prefix + TASK_URLS['change_task_state_agent'].replace('<int:pk>', str(task1.id)),
            {
                'status': TSTATE['In progress'],
                'custom_fields': {},
                'event_point': {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.patch(
            task_prefix + TASK_URLS['change_task_state_agent'].replace('<int:pk>', str(task1.id)),
            {
                'status': TSTATE['Cancelled'],
                'custom_fields': {'reason': 'Client not available'},
                'event_point': {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.patch(
            task_prefix + TASK_URLS['change_task_state_agent'].replace('<int:pk>', str(task2.id)),
            {
                'status': TSTATE['In progress'],
                'custom_fields': {},
                'event_point': {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_complete_task_success(self):
        test_task_complete(self)
        test_task_complete(self)
        test_task_complete(self)
        test_task_complete(self)
        test_task_complete(self)

    def test_execute_task_manager_success(self):
        task1 = create_task('Task_test1', self.manager1, [self.manager1, self.agent12])
        task2 = create_task('Task_test1', self.manager1, [self.manager1])

        client.force_authenticate(self.manager1)
        response = client.patch(
            task_prefix + TASK_URLS['change_task_state_agent'].replace('<int:pk>', str(task1.id)),
            {
                'status': TSTATE['In progress'],
                'custom_fields': {},
                'event_point': {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.patch(
            task_prefix + TASK_URLS['change_task_state_agent'].replace('<int:pk>', str(task1.id)),
            {
                'status': TSTATE['Cancelled'],
                'custom_fields': {'reason': 'Client not available'},
                'event_point': {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.patch(
            task_prefix + TASK_URLS['change_task_state_agent'].replace('<int:pk>', str(task2.id)),
            {
                'status': TSTATE['In progress'],
                'custom_fields': {},
                'event_point': {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_execute_task_agent_fail(self):
        task1 = create_task('Task_test1', self.manager1, [self.agent11, self.agent12])
        task2 = create_task('Task_test2', self.manager1, [self.agent11])
        task3 = create_task('Task_test3', self.manager1, [self.agent13])

        client.force_authenticate(self.agent11)
        response = client.patch(
            task_prefix + TASK_URLS['change_task_state_agent'].replace('<int:pk>', str(task1.id)),
            {
                'status': TSTATE['In progress'],
                'custom_fields': {},
                'event_point': {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # starting multiple task
        response = client.patch(
            task_prefix + TASK_URLS['change_task_state_agent'].replace('<int:pk>', str(task2.id)),
            {
                'status': TSTATE['In progress'],
                'custom_fields': {},
                'event_point': {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        # changing other's task
        response = client.patch(
            task_prefix + TASK_URLS['change_task_state_agent'].replace('<int:pk>', str(task3.id)),
            {
                'status': TSTATE['Cancelled'],
                'custom_fields': {},
                'event_point': {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # cancelling without reason
        response = client.patch(
            task_prefix + TASK_URLS['change_task_state_agent'].replace('<int:pk>', str(task1.id)),
            {
                'status': TSTATE['Cancelled'],
                'custom_fields': {},
                'event_point': {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        task1.image_required = True
        task1.save()

        # without image
        response = client.patch(
            task_prefix + TASK_URLS['change_task_state_agent'].replace('<int:pk>', str(task1.id)),
            {
                'status': TSTATE['Complete'],
                'custom_fields': {'image_urls': ''},
                'event_point': {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

        task1.image_required = False
        task1.save()
        self.agent11.is_present = False
        self.agent11.save()

        response = client.patch(
            task_prefix + TASK_URLS['change_task_state_agent'].replace('<int:pk>', str(task1.id)),
            {
                'status': TSTATE['Complete'],
                'custom_fields': {'image_urls': ''},
                'event_point': {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_get_template_list_success(self):
        client.force_authenticate(self.manager1)

        create_task_template(
            task_type='Retailer Visit',
            task_fields={
                'Shop': '',
                DEMAND_KEYS: DEMAND_TAG_LIST,
                DEMAND_CONTAINER: [],
                'Client Name': ''
            },
            manager=self.manager1
        )

        create_task_template(
            task_type='Doctor Visit',
            task_fields={
                DEMAND_KEYS: DEMAND_TAG_LIST,
                DEMAND_CONTAINER: [],
                'Doctor Name': ''
            },
            manager=self.manager1
        )

        response = client.get(
            task_prefix + TASK_URLS['get_templates'],
            {},
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_create_template_success(self):
        client.force_authenticate(self.manager1)
        response = client.post(
            task_prefix + TASK_URLS['create_template'],
            {
                'user': self.manager1.id,
                'org': self.manager1.org_id,
                'task_type': 'Retailer Visit',
                'task_fields': {
                    'Pharmacy': '',
                    DEMAND_KEYS: DEMAND_TAG_LIST,
                    DEMAND_CONTAINER: [],
                    'Client Name': ''
                },
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 201)
        task = list(TaskTemplate.objects.filter(org=self.manager1.org))[0]
        self.assertEqual(task.task_type, 'Retailer Visit')

    def test_edit_template_success(self):

        template = create_task_template(
            task_type='Retailer Visit',
            task_fields={
                'Shop': '',
                DEMAND_KEYS: DEMAND_TAG_LIST,
                DEMAND_CONTAINER: [],
                'Client Name': ''
            },
            manager=self.manager1
        )
        client.force_authenticate(self.manager1)

        response = client.patch(
            task_prefix + TASK_URLS['edit_template'].replace('<int:pk>', str(template.id)),
            {
                'user': self.manager1.id,
                'org': self.manager1.org_id,
                'task_type': 'Doctor Visit',
                'task_fields': {
                    DEMAND_KEYS: DEMAND_TAG_LIST,
                    DEMAND_CONTAINER: [],
                    'Doctor Name': ''
                },
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        task = list(TaskTemplate.objects.filter(org=self.manager1.org))[0]
        self.assertEqual(task.task_type, 'Doctor Visit')

    def test_delete_template_success(self):

        template = create_task_template(
            task_type='Retailer Visit',
            task_fields={
                'Shop': '',
                DEMAND_KEYS: DEMAND_TAG_LIST,
                DEMAND_CONTAINER: [],
                'Client Name': ''
            },
            manager=self.manager1
        )
        client.force_authenticate(self.manager1)

        response = client.delete(
            task_prefix + TASK_URLS['edit_template'].replace('<int:pk>', str(template.id)),
            {},
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        task = list(TaskTemplate.objects.filter(org=self.manager1.org))
        self.assertEqual(len(task), 0)

    def test_export_task_success(self):
        task1 = create_task('Task_test1', self.manager1, [self.agent11, self.agent12])
        task2 = create_task('Task_test1', self.manager1, [self.agent13])

        client.force_authenticate(self.manager1)

        response = client.get(
            task_prefix + TASK_URLS['export_tasks'],
            {},
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

