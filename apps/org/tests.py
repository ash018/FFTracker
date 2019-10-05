import os
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.org.models import Organization
from apps.user.helpers import create_agent, create_manager, create_organizer
from apps.org.urls import ORG_URLS


User = get_user_model()
client = APIClient()

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
org_prefix = '/v0/org/'
user_prefix = '/v0/user/'

weekend = [4, 5]


class UserTestCase(TestCase):

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

        self.organizer1 = create_organizer(self.username10, 'org1')

        self.manager1 = create_manager(self.username1, self.organizer1, self.organizer1.org)
        self.agent11 = create_agent(self.username2, self.manager1)
        self.agent12 = create_agent(self.username3, self.manager1)
        self.agent13 = create_agent(self.username4, self.manager1)

        self.manager2 = create_manager(self.username5, self.organizer1, self.organizer1.org)
        self.agent21 = create_agent(self.username6, self.manager2)
        self.agent22 = create_agent(self.username7, self.manager2)

    def test_edit_org_success(self):

        client.force_authenticate(self.organizer1)
        response = client.put(
            org_prefix + ORG_URLS['org_org_id'].replace('<int:pk>', str(self.organizer1.org_id)),
            {
                'org_name': 'My Org',
                'address': 'Gulshan, Dhaka',
                'day_start': '09:00:00',
                'day_end': '17:00:00',
                'location_interval': 120,
                'weekend': weekend,
                'tracking_enabled': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        # print(response.data)

    def test_edit_org_fail_invalid_time(self):

        client.force_authenticate(self.organizer1)
        response = client.put(
            org_prefix + ORG_URLS['org_org_id'].replace('<int:pk>', str(self.organizer1.org_id)),
            {
                'org_name': 'My Org',
                'address': 'Gulshan, Dhaka',
                'day_start': '09:00:00',
                'day_end': '09:55:00',
                'location_interval': 120,
                'weekend': weekend,
                'tracking_enabled': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 406)
        # print(response.data)

    def test_get_org_success(self):
        client.force_authenticate(self.organizer1)

        response = client.get(
            org_prefix + ORG_URLS['org_org_id'].replace('<int:pk>', str(self.organizer1.org_id)),
            {
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)

        client.force_authenticate(None)
        client.force_authenticate(self.manager1)
        response = client.get(
            org_prefix + ORG_URLS['org_org_id'].replace('<int:pk>', str(self.organizer1.org_id)),
            {
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        # print(response.data)

    def test_delete_account(self):

        client.force_authenticate(self.organizer1)
        response = client.post(
            org_prefix + ORG_URLS['org_delete'],
            {},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        org = Organization.objects.get(id=self.organizer1.org.id)
        self.assertEqual(org.status, 2)

    def test_user_excel_upload(self):

        client.force_authenticate(self.organizer1)
        self.organizer1.org.subscription.agent_limit = 15
        self.organizer1.org.subscription.save()
        excel = open(os.path.join(FILE_DIR, 'input_files/user_data.xlsx'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_users'],
            {
                'user_data': excel,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

        excel = open(os.path.join(FILE_DIR, 'input_files/user_data.xlsx'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_users'],
            {
                'user_data': excel,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

        excel = open(os.path.join(FILE_DIR, 'input_files/user_data.xlsx'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_users'],
            {
                'user_data': excel,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_user_excel_upload_whitespaces(self):

        client.force_authenticate(self.organizer1)
        self.organizer1.org.subscription.agent_limit = 15
        self.organizer1.org.subscription.save()
        excel = open(os.path.join(FILE_DIR, 'input_files/user_data_whitespaces.xlsx'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_users'],
            {
                'user_data': excel,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_user_excel_upload_fail_hierarchy(self):

        client.force_authenticate(self.organizer1)
        self.organizer1.org.subscription.agent_limit = 15
        self.organizer1.org.subscription.save()
        excel = open(os.path.join(FILE_DIR, 'input_files/user_data_invalid.xlsx'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_users'],
            {
                'user_data': excel,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 406)

    def test_user_excel_upload_fail_agent_limit(self):

        client.force_authenticate(self.organizer1)
        self.organizer1.org.subscription.agent_limit = 8
        self.organizer1.org.subscription.save()
        excel = open(os.path.join(FILE_DIR, 'input_files/user_data.xlsx'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_users'],
            {
                'user_data': excel,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 406)

    def test_user_csv_upload(self):

        client.force_authenticate(self.organizer1)
        self.organizer1.org.subscription.agent_limit = 15
        self.organizer1.org.subscription.save()
        user_csv = open(os.path.join(FILE_DIR, 'input_files/user_data.csv'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_users_csv'],
            {
                'user_data': user_csv,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_user_csv_upload_whitespaces(self):

        client.force_authenticate(self.organizer1)
        self.organizer1.org.subscription.agent_limit = 15
        self.organizer1.org.subscription.save()
        csv_data = open(os.path.join(FILE_DIR, 'input_files/user_data_whitespaces.csv'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_users_csv'],
            {
                'user_data': csv_data,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_user_csv_upload_fail_hierarchy(self):

        client.force_authenticate(self.organizer1)
        self.organizer1.org.subscription.agent_limit = 15
        self.organizer1.org.subscription.save()
        csv_data = open(os.path.join(FILE_DIR, 'input_files/user_data_invalid.csv'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_users_csv'],
            {
                'user_data': csv_data,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 406)

    def test_user_csv_upload_fail_agent_limit(self):

        client.force_authenticate(self.organizer1)
        self.organizer1.org.subscription.agent_limit = 8
        self.organizer1.org.subscription.save()
        csv_data = open(os.path.join(FILE_DIR, 'input_files/user_data.csv'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_users_csv'],
            {
                'user_data': csv_data,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 406)

    def test_task_excel_upload(self):

        client.force_authenticate(self.organizer1)
        excel = open(os.path.join(FILE_DIR, 'input_files/task_data.xlsx'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_tasks'],
            {
                'task_data': excel,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_task_excel_upload_fail_invalid_manager(self):
        client.force_authenticate(self.organizer1)
        excel = open(os.path.join(FILE_DIR, 'input_files/task_data_invalid_manager.xlsx'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_tasks'],
            {
                'task_data': excel,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 406)

    def test_task_excel_upload_fail_invalid_agent(self):
        client.force_authenticate(self.organizer1)
        excel = open(os.path.join(FILE_DIR, 'input_files/task_data_invalid_agent.xlsx'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_tasks'],
            {
                'task_data': excel,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 406)

    def test_task_excel_upload_fail_not_related_agent(self):
        client.force_authenticate(self.organizer1)
        excel = open(os.path.join(FILE_DIR, 'input_files/task_data_not_related_agent.xlsx'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_tasks'],
            {
                'task_data': excel,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 406)

    def test_task_csv_upload(self):

        client.force_authenticate(self.organizer1)
        task_csv = open(os.path.join(FILE_DIR, 'input_files/task_data.csv'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_tasks_csv'],
            {
                'task_data': task_csv,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_task_csv_upload_fail_invalid_manager(self):

        client.force_authenticate(self.organizer1)
        csv_data = open(os.path.join(FILE_DIR, 'input_files/task_data_invalid_manager.csv'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_tasks_csv'],
            {
                'task_data': csv_data,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 406)

    def test_location_excel_upload(self):

        client.force_authenticate(self.organizer1)
        excel = open(os.path.join(FILE_DIR, 'input_files/location_data.xlsx'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_locations'],
            {
                'location_data': excel,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

        response = client.get(
            org_prefix + ORG_URLS['org_client_location'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_location_excel_upload_fail_name(self):

        client.force_authenticate(self.organizer1)
        excel = open(os.path.join(FILE_DIR, 'input_files/location_data_invalid_name.xlsx'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_locations'],
            {
                'location_data': excel,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 406)

    def test_location_excel_upload_fail_lat(self):

        client.force_authenticate(self.organizer1)
        excel = open(os.path.join(FILE_DIR, 'input_files/location_data_invalid_lat.xlsx'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_locations'],
            {
                'location_data': excel,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 406)

    def test_location_csv_upload(self):

        client.force_authenticate(self.organizer1)
        csv_data = open(os.path.join(FILE_DIR, 'input_files/location_data.csv'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_locations_csv'],
            {
                'location_data': csv_data,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

        response = client.get(
            org_prefix + ORG_URLS['org_client_location'],
            {
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_location_csv_upload_fail_name(self):

        client.force_authenticate(self.organizer1)
        csv_data = open(os.path.join(FILE_DIR, 'input_files/location_data_invalid_name.csv'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_locations_csv'],
            {
                'location_data': csv_data,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 406)

    def test_location_csv_upload_fail_lat(self):

        client.force_authenticate(self.organizer1)
        csv_data = open(os.path.join(FILE_DIR, 'input_files/location_data_invalid_lat.csv'), "rb")
        response = client.post(
            org_prefix + ORG_URLS['upload_locations_csv'],
            {
                'location_data': csv_data,
            },
            format='multipart',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 406)




