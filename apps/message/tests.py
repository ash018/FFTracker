import json
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status
from apps.user.helpers import create_agent, create_manager, create_organizer
from apps.message.urls import MSG_ULRS

User = get_user_model()
client = APIClient()

msg_prefix = '/v0/message/'


class MessageTestCase(TestCase):

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

    def test_send_message_flow_success(self):

        client.force_authenticate(self.manager1)
        response = client.post(
            msg_prefix + MSG_ULRS['message_new_thread'],
            {
                'text': 'Hello Agent 11',
                'recipient_id': self.agent11.id,
                'attachments': ['url1', 'url2']
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.post(
            msg_prefix + MSG_ULRS['create_chat_group'],
            {
                'group_name': 'My group',
                'member_list': [self.agent11.id, self.agent12.id],
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = client.get(
            msg_prefix + MSG_ULRS['get_conversations'],
            {},
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        client.force_authenticate(user=None)
        client.force_authenticate(self.agent11)

        response = client.get(
            msg_prefix + MSG_ULRS['get_conversations'],
            {},
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_duplicate_message_thread(self):

        client.force_authenticate(self.manager1)
        response = client.post(
            msg_prefix + MSG_ULRS['message_new_thread'],
            {
                'text': 'Hello Agent 11',
                'recipient_id': self.agent11.id,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.post(
            msg_prefix + MSG_ULRS['message_new_thread'],
            {
                'text': 'Agent 12, get the work done!',
                'recipient_id': self.agent12.id,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.post(
            msg_prefix + MSG_ULRS['message_new_thread'],
            {
                'text': 'Where are you 11?',
                'recipient_id': self.agent11.id,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # print('Manager 1 conversations........')
        response = client.get(
            msg_prefix + MSG_ULRS['get_conversations'],
            {},
            format='json',
        )
        # print(json.dumps(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        client.force_authenticate(user=None)
        client.force_authenticate(self.agent11)

        response = client.post(
            msg_prefix + MSG_ULRS['message_new_thread'],
            {
                'text': 'Hello Manager 1',
                'recipient_id': self.manager1.id,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # print('Conversations of agent 1........')
        response = client.get(
            msg_prefix + MSG_ULRS['get_conversations'],
            {},
            format='json',
        )
        # print(json.dumps(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # print('All messages of agent 1 from first thread........')

        thread_id = response.data[0]['thread_id']
        response = client.get(
            msg_prefix + MSG_ULRS['get_messages'].replace('<int:thread_id>', str(thread_id)),
            {},
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_user_list(self):

        client.force_authenticate(self.manager1)
        response = client.get(
            msg_prefix + MSG_ULRS['user_list'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

        client.force_authenticate(None)
        client.force_authenticate(self.agent11)
        response = client.get(
            msg_prefix + MSG_ULRS['user_list'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

