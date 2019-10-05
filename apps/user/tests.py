import json
from django.test import TestCase
from django.utils import timezone
import uuid
from rest_framework.test import APIClient
from rest_framework import status

from apps.user.config import ROLE_DICT

from apps.user.models import User
from apps.user.auth_helpers import create_username
from apps.user.helpers import create_agent, create_manager, create_organizer
from apps.user.urls import USER_ULRS
from apps.task.config import TASK_STATUS_DICT as TSTATE
from apps.task.helpers import create_task
from apps.common.models import AppInfo

client = APIClient()

user_prefix = '/v0/user/'
org_prefix = '/v0/org/'


def set_duration(hours=2):
    return timezone.now() + timezone.timedelta(hours=hours)


def upload_data(inst, mb, user, mac):
    client.force_authenticate(None)
    client.force_authenticate(user)
    response = client.post(
        user_prefix + USER_ULRS['data_usage'],
        {
            'mac': mac,
            'megabytes': mb
        },
        format='json',
    )
    inst.assertEqual(response.status_code, status.HTTP_200_OK)


FB_TOKEN_VALID = 'EAADPOQXWzvgBAJPDI7EcqpnC2B1hELlre2xQPSsZBwgBoI1oVAF8yho7243NZCTAgyC1Y9co6MAKfGa2ZBgfwWXr92eDZCy5LZAs5c0GQifCvyrE9b9DXVc7OiZAkCG1yC3171CWYpQp1XQ0qF744ZAEvZBKxl26x7Yr9ibJvWEHAwZDZD'
FB_TOKEN_INVALID = 'EAADPOQXWzvgBAJPDI7EcqpnC2B1hELlre2xQPSsZBwgBoI1oVAF8yho7243NZCTAgyC1Y9co6MAKfGa2ZBgfwWXr92eDZCy5LZAs5c0GQifCvyrE9b9DXVc7OiZAkCG1yC3171CWYpQp1XQ0qF744ZAEvZBKxl26x7Yr9ibJvWEHAwZDZD'


class UserTestCase(TestCase):

    def setUp(self):
        self.valid_access_token1 = 'EMAWd6pxUXs2pZAyHQFxVr3i3ZArx5sUdNu0LxzSBV98SVDVXNruFqsHpZCHfe6h5KJVKkzLpduU8r0F4gQGWDhbuUVMjb4lGaMKFBCiQybF7tLvyEdOMmF7uUhhITRQZBGWPBMZBAVBPk09kbTWn7j91yKWY6CJCUZD'
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

        self.username20 = 'username20'

        self.organizer1 = create_organizer(self.username11, 'org1')
        self.organizer2 = create_organizer(self.username12, 'org2')

    # def test_signup_success(self):
    #
    #     response = client.post(
    #         user_prefix + USER_ULRS['signup_api'],
    #         {
    #             'oid': 'neworg',
    #             'username': 'newuser',
    #             'access_token': FB_TOKEN_VALID,
    #         },
    #         format='json',
    #     )
    #     print(response.data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_signup_fail_invalid_username(self):

        response = client.post(
            user_prefix + USER_ULRS['signup_api'],
            {
                'oid': 'neworg',
                'username': 'new user',
                'access_token': FB_TOKEN_VALID,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_signup_fail_invalid_org(self):

        response = client.post(
            user_prefix + USER_ULRS['signup_api'],
            {
                'oid': 'new@org',
                'username': 'newuser',
                'access_token': FB_TOKEN_VALID,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_signup_fail_invalid_token(self):
        # TODO: Add token generator class for authkit
        response = client.post(
            user_prefix + USER_ULRS['signup_api'],
            {
                'oid': 'neworg',
                'username': 'new user',
                'access_token': FB_TOKEN_INVALID,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_login_success(self):
        manager1 = create_manager(self.username1, self.organizer1, self.organizer1.org)
        password = '1234567890'
        manager1.set_password(password)
        manager1.save()

        response = client.post(
            user_prefix + USER_ULRS['login_password'],
            {
                'oid': manager1.org.oid,
                'username': self.username1,
                'password': password,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

        oid_upper = manager1.org.oid.upper()
        # print(oid_upper)
        response = client.post(
            user_prefix + USER_ULRS['login_password'],
            {
                'oid': oid_upper,
                'username': self.username1,
                'password': password,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

        response = client.post(
            user_prefix + USER_ULRS['login_password'],
            {
                'oid': manager1.org.oid,
                'username': self.username1,
                'password': 'wrong_pass',
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 401)

    def test_set_password_success(self):
        manager = create_manager(self.username1, self.organizer1, self.organizer1.org)

        password = '1234567890'

        client.force_authenticate(manager)
        response = client.post(
            user_prefix + USER_ULRS['set_password'],
            {
                'password': password,
            },
            format='json',
        )
        # print('Password set response: ' + str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_success(self):
        manager1 = create_manager(self.username1, self.organizer1, self.organizer1.org)
        password = '1234567890'
        manager1.set_password(password)
        manager1.save()

        client.force_authenticate(manager1)
        response = client.post(
            user_prefix + USER_ULRS['change_password'],
            {
                'old_password': password,
                'new_password': 'new_password',
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        manager1.refresh_from_db()
        self.assertEqual(manager1.check_password('new_password'), True)

    def test_change_password_fail(self):
        manager1 = create_manager(self.username1, self.organizer1, self.organizer1.org)
        password = '1234567890'
        manager1.set_password(password)

        client.force_authenticate(manager1)
        response = client.post(
            user_prefix + USER_ULRS['change_password'],
            {
                'old_password': password,
                'new_password': '1234567',
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_edit_profile_success(self):
        manager1 = create_manager(self.username1, self.organizer1, self.organizer1.org)

        client.force_authenticate(user=manager1)
        response = client.patch(
            user_prefix + USER_ULRS['profile_id'].replace('<int:pk>', str(manager1.id)),
            {
                'full_name': 'Manager1',
                'phone': '+8801788000000',
                'email': 'newemail@gma.com',
                'designation': 'AGM Dhaka Zone',
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.patch(
            user_prefix + USER_ULRS['profile_id'].replace('<int:pk>', str(manager1.id)),
            {
                'full_name': 'Manager1',
                'username': self.username10,
                'phone': '+8801788000000',
                'email': 'newemail@gma.com',
                'designation': 'AGM Dhaka Zone',
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        manager1.refresh_from_db()
        self.assertEqual(manager1.username, create_username(manager1.org.oid, self.username10))

    def test_create_account_success(self):
        organizer1 = self.organizer1
        client.force_authenticate(organizer1)
        response = client.post(
            user_prefix + USER_ULRS['account'],
            {
                'username': self.username2,
                'full_name': 'agent1',
                'designation': 'AGM',
                'parent': organizer1.id,
                'role': ROLE_DICT['Employee'],
                'org': organizer1.org.id,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        organizer2 = self.organizer2
        client.force_authenticate(None)
        client.force_authenticate(organizer2)
        response = client.post(
            user_prefix + USER_ULRS['account'],
            {
                'username': self.username2,
                'full_name': 'agent1',
                'designation': 'AGM',
                'parent': organizer2.id,
                'role': ROLE_DICT['Employee'],
                'org': organizer2.org.id,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_account_fail_username(self):
        manager = create_manager(self.username1, self.organizer1, self.organizer1.org)
        agent = create_agent(self.username2, manager)

        client.force_authenticate(self.organizer1)
        response = client.post(
            user_prefix + USER_ULRS['account'],
            {
                'username': self.username2,
                'full_name': 'agent1',
                'designation': 'AGM',
                'parent': manager.id,
                'role': ROLE_DICT['Employee'],
                'org': manager.org.id,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 406)

    def test_get_profile_success(self):
        manager = create_manager(self.username1, self.organizer1, self.organizer1.org)
        AppInfo.objects.create(
            current_version=10, app_name='manager'
        )

        AppInfo.objects.create(
            current_version=11, app_name='agent'
        )

        client.force_authenticate(manager)
        response = client.get(
            user_prefix + USER_ULRS['profile_id'].replace('<int:pk>', str(manager.id)),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['current_version'], 10)

        # print(json.dumps(response.data))
        agent = create_agent(self.username2, manager)

        client.force_authenticate(None)
        client.force_authenticate(agent)
        response = client.get(
            user_prefix + USER_ULRS['profile_id'].replace('<int:pk>', str(agent.id)),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['current_version'], 11)

    def test_get_account_success(self):
        manager = create_manager(self.username1, self.organizer1, self.organizer1.org)

        agent = create_agent(self.username2, manager)

        client.force_authenticate(manager)
        response = client.get(
            user_prefix + USER_ULRS['account_id'].replace('<int:pk>', str(agent.id)),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_account_fail_org(self):
        manager1 = create_manager(self.username1, self.organizer1, self.organizer1.org)
        manager2 = create_manager(self.username1, self.organizer2, self.organizer2.org)
        agent = create_agent(self.username3, manager2)

        client.force_authenticate(manager1)
        response = client.get(
            user_prefix + USER_ULRS['account_id'].replace('<int:pk>', str(agent.id)),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_account_list(self):

        manager1 = create_manager(self.username1, None, self.organizer1.org)
        manager11 = create_manager(self.username2, manager1, self.organizer1.org)
        agent11 = create_agent(self.username3, manager1)

        manager111 = create_manager(self.username7, manager11, self.organizer1.org)
        agent111 = create_agent(self.username8, manager11)
        agent112 = create_agent(self.username9, manager11)

        manager2 = create_manager(self.username4, self.organizer1, self.organizer1.org)
        manager21 = create_manager(self.username5, manager2, self.organizer1.org)
        agent22 = create_agent(self.username6, manager2)

        manager3 = create_manager(self.username20, None, self.organizer1.org)

        client.force_authenticate(manager1)

        response = client.get(
            user_prefix + USER_ULRS['account'],
            {

            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 6)

        response = client.get(
            user_prefix + USER_ULRS['account'],
            {
                'role': ROLE_DICT['Manager']
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        client.force_authenticate(None)
        client.force_authenticate(self.organizer1)

        response = client.get(
            user_prefix + USER_ULRS['account'],
            {
                'role': ROLE_DICT['Manager']
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 6)

        response = client.get(
            user_prefix + USER_ULRS['account'],
            {
                'manager_id': manager11.id
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        response = client.get(
            user_prefix + USER_ULRS['account'],
            {
                'manager_id': self.organizer1.id
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print(response.data)
        self.assertEqual(len(response.data), 2)

    def test_get_resource_list_success(self):
        manager1 = create_manager(self.username1, self.organizer1, self.organizer1.org)
        agent11 = create_agent(self.username2, manager1)
        agent12 = create_agent(self.username3, manager1)

        task1 = create_task('Task_test1', manager1, [agent11, agent12], status=TSTATE['In progress'])

        client.force_authenticate(manager1)
        response = client.get(
            user_prefix + USER_ULRS['resource_list'],
            {
                'status': 'working'
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        client.force_authenticate(None)
        client.force_authenticate(self.organizer1)
        response = client.get(
            user_prefix + USER_ULRS['resource_list'],
            {
                'status': 'working'
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        # print(response.data)

    def test_edit_account_success(self):
        manager = create_manager(self.username1, self.organizer1, self.organizer1.org)
        agent = create_agent(self.username3, manager)

        client.force_authenticate(self.organizer1)
        response = client.patch(
            user_prefix + USER_ULRS['account_id'].replace('<int:pk>', str(agent.id)),
            {
                'username': self.username4,
                'full_name': 'agent1',
                'parent': manager.id,
                'role': ROLE_DICT['Employee'],
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        agent = User.objects.get(id=agent.id)
        self.assertEqual(agent.username, create_username(agent.org.oid, self.username4))

    def test_change_manger_success(self):
        manager = create_manager(self.username1, self.organizer1, self.organizer1.org)
        manager2 = create_manager(self.username5, self.organizer1, self.organizer1.org)
        agent = create_agent(self.username2, manager)

        client.force_authenticate(self.organizer1)
        response = client.patch(
            user_prefix + USER_ULRS['account_id'].replace('<int:pk>', str(agent.id)),
            {
                'username': self.username2,
                'full_name': 'agent1',
                'parent': manager2.id,
                'role': ROLE_DICT['Employee'],
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_set_manger_none_success(self):
        manager = create_manager(self.username1, self.organizer1, self.organizer1.org)
        agent = create_agent(self.username2, manager)

        client.force_authenticate(self.organizer1)
        response = client.patch(
            user_prefix + USER_ULRS['account_id'].replace('<int:pk>', str(agent.id)),
            {
                'username': self.username2,
                'full_name': 'agent1',
                'parent': None,
                'role': ROLE_DICT['Employee'],
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_account_fail_username_exists(self):
        manager = create_manager(self.username1, self.organizer1, self.organizer1.org)
        agent = create_agent(self.username3, manager)
        agent2 = create_agent(self.username4, manager)

        client.force_authenticate(self.organizer1)
        response = client.patch(
            user_prefix + USER_ULRS['account_id'].replace('<int:pk>', str(agent.id)),
            {
                'username': self.username4,
                'full_name': 'agent1',
                'parent': manager.id,
                'role': ROLE_DICT['Employee'],
                'org': manager.org.id,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 406)

    def test_edit_account_fail_username_with_spaces(self):
        manager = create_manager(self.username1, self.organizer1, self.organizer1.org)
        agent = create_agent(self.username3, manager)
        agent2 = create_agent(self.username4, manager)

        client.force_authenticate(self.organizer1)
        response = client.patch(
            user_prefix + USER_ULRS['account_id'].replace('<int:pk>', str(agent.id)),
            {
                'username': 'A User1',
                'full_name': 'agent1',
                'parent': manager.id,
                'role': ROLE_DICT['Employee'],
                'org': manager.org.id,
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_delete_account_success(self):
        manager = create_manager(self.username1, self.organizer1, self.organizer1.org)
        agent = create_agent(self.username3, manager)

        client.force_authenticate(self.organizer1)
        response = client.delete(
            user_prefix + USER_ULRS['account_id'].replace('<int:pk>', str(agent.id)),
            {},
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.filter(phone=self.username3).exists(), False)

    def test_fb_token_update_success(self):
        manager = create_manager(self.username1, self.organizer1, self.organizer1.org)
        token = uuid.uuid4()

        client.force_authenticate(manager)
        response = client.post(
            user_prefix + USER_ULRS['update_fb_token'],
            {
                'fb_token': token,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print(response.data)

    def test_get_dashboard_success(self):
        '''Team1 details'''
        manager1 = create_manager(self.username1, self.organizer1, self.organizer1.org)
        agent1 = create_agent(self.username2, manager1)
        agent2 = create_agent(self.username3, manager1)
        agent3 = create_agent(self.username4, manager1)
        agent4 = create_agent(self.username5, manager1)

        task1 = create_task('Retailer 1', manager1, [agent1, agent2], status=TSTATE['In progress'])
        task2 = create_task('Doctor Visit', manager1, [agent2])
        task3 = create_task('Survey 1', manager1, [agent3])
        task3.delayed = True
        task3.save()
        task4 = create_task('Survey 2', manager1, [agent4], status=TSTATE['Cancelled'])

        '''Team2 details'''
        manager2 = create_manager(self.username6, self.organizer1, self.organizer1.org)
        agent5 = create_agent(self.username7, manager2)

        task5 = create_task('Demand Collection', manager2, [agent5], status=TSTATE['In progress'])
        task5 = create_task('Delivery', manager2, [agent5], status=TSTATE['Cancelled'])

        client.force_authenticate(manager1)
        response = client.get(
            user_prefix + USER_ULRS['search_api_manager'].replace('<str:token>', 'survey'),
            {},
            format='json',
        )

        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        client.force_authenticate(user=None)
        client.force_authenticate(manager2)
        response = client.get(
            user_prefix + USER_ULRS['manager_dashboard'],
            {},
            format='json',
        )

        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        client.force_authenticate(user=None)
        client.force_authenticate(agent2)
        response = client.get(
            user_prefix + USER_ULRS['agent_dashboard'],
            {},
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['current_task']), 1)
        self.assertEqual(response.data['current_task'][0]['title'], 'Retailer 1')

    def test_search_account_light_success(self):
        manager = create_manager(self.username1, self.organizer1, self.organizer1.org)
        agent1 = create_agent(self.username3, manager)
        agent2 = create_agent(self.username4, manager)
        agent3 = create_agent('halios', manager)

        client.force_authenticate(self.organizer1)
        response = client.get(
            user_prefix + USER_ULRS['search_user'].replace('<str:token>', 'user'),
            {},
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_search_account_in_list_success(self):
        manager = create_manager(self.username1, self.organizer1, self.organizer1.org)
        agent1 = create_agent(self.username3, manager)
        agent2 = create_agent(self.username4, manager)
        agent3 = create_agent('halios', manager)

        client.force_authenticate(self.organizer1)
        response = client.get(
            user_prefix + USER_ULRS['accounts_paginated'],
            {
                'token': ''
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)

        client.force_authenticate(self.organizer1)
        response = client.get(
            user_prefix + USER_ULRS['accounts_paginated'],
            {
                'token': 'username'
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_data_usage_upload_success(self):
        manager = create_manager(self.username1, self.organizer1, self.organizer1.org)
        agent1 = create_agent(self.username3, manager)
        agent2 = create_agent(self.username4, manager)

        mb_list1 = [0.5, 1.5, 0.5, 1.5, 2.0]
        # total1 = .5 + 1 + .5 + 1 + .5 = 3.5

        mb_list2 = [7.5, 8.5, 0.5, 1.5, 2.0]
        # total2 = 7.5 + 1 + .5 + 1 + .5 = 10.5

        for mb in mb_list1:
            upload_data(self, mb, agent1, '00:0a:95:9d:68:16')

        for mb in mb_list2:
            upload_data(self, mb, agent1, '00:0a:95:9d:68:17')

        for mb in mb_list1:
            upload_data(self, mb, agent2, '00:0a:95:9d:68:18')

        client.force_authenticate(None)
        client.force_authenticate(manager)
        response = client.get(
            user_prefix + USER_ULRS['data_usage'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        response = client.get(
            user_prefix + USER_ULRS['data_usage_id'].replace('<int:agent_id>', str(agent1.id)),
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['megabytes'], 14.0)


