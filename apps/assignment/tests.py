from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.user.helpers import create_agent, create_manager, create_organizer
from apps.assignment.models import Assignment, Comment
from apps.assignment.config import ASSIGNMENT_STATUS_DICT as ASD
from apps.assignment.urls import ASSIGNMENT_URLS
from .helpers import create_assignment

User = get_user_model()
client = APIClient()
assignment_prefix = '/v0/assignment/'
user_prefix = '/v0/user/'

deadline = "2019-03-11T07:07:24.000000+00:00"


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

    def test_create_assignment_success(self):
        client.force_authenticate(self.manager1)

        response = client.post(
            assignment_prefix + ASSIGNMENT_URLS['assignment'],
            {
                'title': 'Assignment1',
                'manager': self.manager1.id,
                'description': 'Retailer Visit',
                'deadline': deadline,
                'assignee': self.agent12.id,
                'org': self.manager1.org.id,
                'custom_fields': {
                    'target1': 50,
                    'name': 'Manager'
                }
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = client.post(
            assignment_prefix + ASSIGNMENT_URLS['assignment'],
            {
                'title': 'Assignment1',
                'manager': self.manager1.id,
                'description': 'Retailer Visit',
                'deadline': deadline,
                'org': self.manager1.org.id,
                'custom_fields': {
                    'target1': 50,
                    'name': 'Manager'
                }
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = client.post(
            assignment_prefix + ASSIGNMENT_URLS['assignment'],
            {
                'title': 'Assignment1',
                'manager': self.manager1.id,
                'description': 'Retailer Visit',
                'deadline': deadline,
                'assignee': None,
                'org': self.manager1.org.id,
                'custom_fields': {
                    'target1': 50,
                    'name': 'Manager'
                }
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assignment = list(Assignment.objects.filter(manager=self.manager1))[0]
        self.assertEqual(assignment.title, 'Assignment1')

        response = client.post(
            assignment_prefix + ASSIGNMENT_URLS['assignment'],
            {
                'title': 'Assignment2',
                'manager': self.manager1.id,
                'description': 'Retailer Visit',
                'deadline': deadline,
                'org': self.manager1.org.id,
                'custom_fields': {
                    'target1': 50,
                    'name': 'Manager'
                }
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_assignment_success(self):
        assignment = create_assignment(self.manager1, [self.agent13])

        client.force_authenticate(self.manager1)
        response = client.get(
            assignment_prefix + ASSIGNMENT_URLS['assignment_id'].replace('<int:pk>', str(assignment.id)),
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], assignment.title)

        client.force_authenticate(user=None)
        client.force_authenticate(self.agent13)
        response = client.get(
            assignment_prefix + ASSIGNMENT_URLS['assignment_id'].replace('<int:pk>', str(assignment.id)),
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], assignment.title)

    def test_filter_assignment_success(self):
        assignment1 = create_assignment(self.manager1, [self.agent11], title='Project Alpha')
        assignment2 = create_assignment(self.manager1, [self.agent11], status=ASD['In progress'], title='Target Beta')
        assignment3 = create_assignment(self.manager1, [self.agent12], title='Project Gama')
        assignment4 = create_assignment(self.manager1, [self.agent13], title='Target Delta')
        assignment5 = create_assignment(self.manager1, [self.agent14], title='Target Sigma')
        assignment6 = create_assignment(self.manager2, [self.agent21], title='Batch 1')
        assignment7 = create_assignment(self.manager2, [self.agent22], title='Lot V')

        client.force_authenticate(self.organizer1)
        response = client.get(
            assignment_prefix + ASSIGNMENT_URLS['assignment'],
            {
                'manager_id': self.manager1.id
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

        response = client.get(
            assignment_prefix + ASSIGNMENT_URLS['assignment'],
            {
                'manager_id': self.manager1.id,
                'status': ASD['In progress']
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        client.force_authenticate(None)
        client.force_authenticate(self.manager1)
        response = client.get(
            assignment_prefix + ASSIGNMENT_URLS['assignment'],
            {
                'assignee_id': self.agent11.id
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        response = client.get(
            assignment_prefix + ASSIGNMENT_URLS['assignments_paginated'],
            {
                'assignee_id': self.agent11.id
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

        response = client.get(
            assignment_prefix + ASSIGNMENT_URLS['assignments_paginated'],
            {
                'token': 'target'
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_edit_assignment_success(self):
        client.force_authenticate(self.manager1)
        assignment = create_assignment(self.manager1, [self.agent13])

        response = client.patch(
            assignment_prefix + ASSIGNMENT_URLS['assignment_id'].replace('<int:pk>', str(assignment.id)),
            {
                'title': 'Assignment1',
                'manager': self.manager1.id,
                'description': 'Retailer Visit',
                'deadline': deadline,
                'assignee_list': [self.agent12.id],
                'org': self.manager1.org.id,
                'custom_fields': {
                    'target1': 50,
                    'name': 'Manager'
                }
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_progress_success(self):
        client.force_authenticate(self.manager1)
        assignment = create_assignment(self.manager1, [self.agent13])

        response = client.post(
            assignment_prefix + ASSIGNMENT_URLS['assignment_progress'].replace(
                '<int:pk>', str(assignment.id)
            ),
            {
                'progress': 60,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_assignment_fail(self):
        assignment = create_assignment(self.manager1, [self.agent13], status=ASD['In progress'])

        client.force_authenticate(self.manager2)
        response = client.patch(
            assignment_prefix + ASSIGNMENT_URLS['assignment_id'].replace('<int:pk>', str(assignment.id)),
            {
                'title': 'Assignment1',
                'manager': self.manager1.id,
                'description': 'Retailer Visit',
                'deadline': deadline,
                'assignee_list': [self.agent12.id],
                'org': self.manager1.org.id,
                'custom_fields': {
                    'target1': 50,
                    'name': 'Manager'
                }
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 403)

    def test_get_assignment_list(self):
        assignment1 = create_assignment(self.manager1, [self.agent11])
        assignment2 = create_assignment(self.manager1, [self.agent12], status=ASD['In progress'])
        # assignment3 = create_assignment(self.manager1, [self.agent13])

        assignment4 = create_assignment(self.manager2, [self.agent21])
        assignment5 = create_assignment(self.manager2, [self.agent22])

        client.force_authenticate(self.manager1)
        response = client.post(
            assignment_prefix + ASSIGNMENT_URLS['assignment'],
            {
                'title': 'Assignment1',
                'manager': self.manager1.id,
                'description': 'Retailer Visit',
                'deadline': deadline,
                'assignee': self.agent13.id,
                'org': self.manager1.org.id,
                'custom_fields': {
                    'target1': 50,
                    'name': 'Manager'
                }
            },
            format='json',
        )
        response = client.get(
            assignment_prefix + ASSIGNMENT_URLS['assignment'],
            {
                # 'status': ASD['In progress'],
                # 'agent_id': self.agent11.id
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        response = client.get(
            assignment_prefix + ASSIGNMENT_URLS['assignment'],
            {
                'assignee_id': self.agent13.id
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        client.force_authenticate(None)
        client.force_authenticate(self.agent13)
        response = client.get(
            assignment_prefix + ASSIGNMENT_URLS['assignment'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_add_comment_success(self):
        assignment1 = create_assignment(self.manager1, [self.agent11])
        assignment2 = create_assignment(self.manager1, [self.agent12], status=ASD['In progress'])

        client.force_authenticate(self.manager1)
        response = client.post(
            assignment_prefix + ASSIGNMENT_URLS['comment'],
            {
                'text': 'test comment',
                'attachments': ['url1', 'url2'],
                'user': self.manager1.id,
                'assignment': assignment1.id,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 201)

        client.force_authenticate(None)
        client.force_authenticate(self.agent12)
        response = client.post(
            assignment_prefix + ASSIGNMENT_URLS['comment'],
            {
                'text': 'test comment',
                'attachments': ['url1', 'url2'],
                'user': self.manager1.id,
                'assignment': assignment2.id,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 201)

    def test_comment_sequence_success(self):
        assignment1 = create_assignment(self.manager1, [self.agent12], status=ASD['In progress'])

        client.force_authenticate(self.manager1)
        response = client.post(
            assignment_prefix + ASSIGNMENT_URLS['comment'],
            {
                'text': 'test comment 1',
                'attachments': ['url1', 'url2'],
                'user': self.manager1.id,
                'assignment': assignment1.id,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 201)

        response = client.post(
            assignment_prefix + ASSIGNMENT_URLS['comment'],
            {
                'text': 'test comment 2',
                'attachments': ['url1', 'url2'],
                'user': self.manager1.id,
                'assignment': assignment1.id,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 201)

        response = client.get(
            assignment_prefix + ASSIGNMENT_URLS['assignment_id'].replace('<int:pk>', str(assignment1.id)),
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment_list'][0]['text'], 'test comment 1')
