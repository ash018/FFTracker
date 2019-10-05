from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.user.helpers import create_agent, create_manager, create_organizer
from .helpers import create_notification
from .urls import NTF_ULRS
from .config import NOTIFICATION_DICT as NTD

User = get_user_model()
client = APIClient()

msg_prefix = '/v0/notification/'


class NotificationTestCase(TestCase):

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

        self.ntf1 = create_notification(self.agent11, NTD['SOS'], [self.manager1])
        self.ntf2 = create_notification(self.agent12, NTD['Unreachable'], [self.manager1])
        self.ntf3 = create_notification(self.agent13, NTD['Deadline crossed'], [self.agent13, self.manager1])
        self.ntf4 = create_notification(None, NTD['New Task'], [self.agent13])
        self.ntf5 = create_notification(self.agent14, NTD['Task started'], [self.manager1])

        self.ntf6 = create_notification(self.agent11, NTD['SOS'], [self.manager1])
        self.ntf7 = create_notification(self.agent12, NTD['Unreachable'], [self.manager1])
        self.ntf8 = create_notification(self.agent13, NTD['Deadline crossed'], [self.agent13, self.manager1])
        self.ntf9 = create_notification(None, NTD['New Task'], [self.agent13])
        self.ntf10 = create_notification(self.agent14, NTD['Task started'], [self.manager1])

        self.ntf11 = create_notification(self.agent11, NTD['SOS'], [self.manager1])
        self.ntf12 = create_notification(self.agent12, NTD['Unreachable'], [self.manager1])
        self.ntf13 = create_notification(self.agent13, NTD['Deadline crossed'], [self.agent13, self.manager1])
        self.ntf14 = create_notification(None, NTD['New Task'], [self.agent13])
        self.ntf15 = create_notification(self.agent14, NTD['Task started'], [self.manager1])

    def test_get_notifications(self):

        client.force_authenticate(self.manager1)

        response = client.get(
            msg_prefix + NTF_ULRS['get_notifications_paginated'] + '?limit=5&offset=10',
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

        response = client.get(
            msg_prefix + NTF_ULRS['get_notifications'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 12)

        client.force_authenticate(None)
        client.force_authenticate(self.agent13)

        response = client.get(
            msg_prefix + NTF_ULRS['get_notifications'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 6)

    def test_get_count(self):

        client.force_authenticate(self.manager1)
        response = client.get(
            msg_prefix + NTF_ULRS['get_count'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unchecked'], 12)
        self.assertEqual(response.data['total'], 12)

        client.force_authenticate(None)
        client.force_authenticate(self.agent13)

        response = client.get(
            msg_prefix + NTF_ULRS['get_count'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.data['unchecked'], 6)
        self.assertEqual(response.data['total'], 6)

    def test_mark_read(self):

        client.force_authenticate(self.manager1)
        response = client.post(
            msg_prefix + NTF_ULRS['mark_all_read'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

        response = client.get(
            msg_prefix + NTF_ULRS['get_count'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unchecked'], 0)
        self.assertEqual(response.data['total'], 12)

        client.force_authenticate(None)
        client.force_authenticate(self.agent13)

        response = client.get(
            msg_prefix + NTF_ULRS['get_count'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.data['unchecked'], 6)
        self.assertEqual(response.data['total'], 6)

    def test_set_count(self):

        client.force_authenticate(self.manager1)
        response = client.post(
            msg_prefix + NTF_ULRS['set_count'].replace('<int:pk>', str(self.ntf1.id)),
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

        response = client.get(
            msg_prefix + NTF_ULRS['get_count'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unchecked'], 11)
        self.assertEqual(response.data['total'], 12)

        client.force_authenticate(None)
        client.force_authenticate(self.agent13)

        response = client.get(
            msg_prefix + NTF_ULRS['get_count'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.data['unchecked'], 6)
        self.assertEqual(response.data['total'], 6)

    def test_create_sos(self):

        client.force_authenticate(self.agent11)
        response = client.post(
            msg_prefix + NTF_ULRS['create_notifications'],
            {
                'text': self.agent11.full_name + ' Has sent SOS!',
                'type': NTD['SOS'],
                'agent': self.agent11.id,
                'images': ['url1..', 'url2..'],
                'point': {'lat': 23.780926, 'lng': 90.422858}
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 201)

        client.force_authenticate(None)
        client.force_authenticate(self.manager1)
        response = client.get(
            msg_prefix + NTF_ULRS['get_count'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unchecked'], 13)

        client.force_authenticate(None)
        client.force_authenticate(self.organizer1)
        response = client.get(
            msg_prefix + NTF_ULRS['get_count'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unchecked'], 1)
