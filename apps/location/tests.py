from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.user.helpers import create_agent, create_manager, create_organizer
from apps.task.helpers import create_task
from apps.task.config import TASK_STATUS_DICT as TSTATE
from .config import EVENT_DICT
from apps.location.urls import LOC_URLS
User = get_user_model()
client = APIClient()

location_prefix = '/v0/location/'


def set_duration(hours=2):
    return timezone.now() + timezone.timedelta(hours=hours)


class LocationTestCase(TestCase):

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

    def test_upload_location_agent_success(self):
        task1 = create_task('Task2', self.manager1, [self.agent11], status=TSTATE['In progress'])

        client.force_authenticate(self.agent11)
        response = client.post(
            location_prefix + LOC_URLS['upload_location_api'],
            {
                'event': EVENT_DICT['On Task'],
                'mac': '00:0a:95:9d:68:16',
                'point': {'lat': 23.780926, 'lng': 90.422858},
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        client.force_authenticate(user=None)
        client.force_authenticate(self.agent12)
        response = client.post(
            location_prefix + LOC_URLS['upload_location_api'],
            {
                'event': EVENT_DICT['No Task'],
                'mac': '00:0a:95:9d:68:17',
                'point': {'lat': 23.780926, 'lng': 90.422858},
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        client.force_authenticate(user=None)
        client.force_authenticate(self.agent13)
        response = client.post(
            location_prefix + LOC_URLS['upload_location_api'],
            {
                'event': EVENT_DICT['No Task'],
                'mac': '00:0a:95:9d:68:18',
                'point': {'lat': 23.780926, 'lng': 90.422858},
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        client.force_authenticate(user=None)
        client.force_authenticate(self.manager1)
        response = client.get(
            location_prefix + LOC_URLS['get_resource_locations'],
            {},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print(response.data)

    def test_upload_location_upload_while_offline(self):

        self.agent12.is_present = False
        self.agent12.save()

        client.force_authenticate(self.agent12)
        response = client.post(
            location_prefix + LOC_URLS['upload_location_api'],
            {
                'event': EVENT_DICT['On Task'],
                'mac': '00:0a:95:9d:68:16',
                'point': {'lat': 23.780926, 'lng': 90.422858},
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertEqual(response.data['detail'], 'invalid_upload')

    def test_attendance_flow(self):

        client.force_authenticate(self.agent11)
        self.agent11.is_present = False
        self.agent11.save()

        response = client.post(
            location_prefix + LOC_URLS['upload_location_api'],
            {
                'event': EVENT_DICT['To Online'],
                'mac': '00:0a:95:9d:68:16',
                'point': {'lat': 23.780926, 'lng': 90.422858},
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.agent11.refresh_from_db()
        self.assertEqual(self.agent11.is_present, True)

        response = client.post(
            location_prefix + LOC_URLS['upload_location_api'],
            {
                'event': EVENT_DICT['To Offline'],
                'mac': '00:0a:95:9d:68:16',
                'point': {'lat': 23.780926, 'lng': 90.422858},
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.agent11.refresh_from_db()
        self.assertEqual(self.agent11.is_present, False)

    def test_attendance_flow_not_fail_active_task(self):
        client.force_authenticate(self.agent11)

        task1 = create_task('Task2', self.manager1, [self.agent11], status=TSTATE['In progress'])

        response = client.post(
            location_prefix + LOC_URLS['upload_location_api'],
            {
                'event': EVENT_DICT['To Offline'],
                'mac': '00:0a:95:9d:68:16',
                'point': {'lat': 23.780926, 'lng': 90.422858},
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.agent11.refresh_from_db()
        self.assertEqual(self.agent11.is_present, False)

    def test_attendance_flow_fail_sequence(self):

        self.agent11.is_present = False
        self.agent11.save()
        client.force_authenticate(self.agent11)

        response = client.post(
            location_prefix + LOC_URLS['upload_location_api'],
            {
                'event': EVENT_DICT['To Offline'],
                'mac': '00:0a:95:9d:68:16',
                'point': {'lat': 23.780926, 'lng': 90.422858},
            },
            format='json',
        )

        self.assertEqual(response.status_code, 406)

        self.agent11.is_present = True
        self.agent11.save()

        response = client.post(
            location_prefix + LOC_URLS['upload_location_api'],
            {
                'event': EVENT_DICT['To Online'],
                'mac': '00:0a:95:9d:68:16',
                'point': {'lat': 23.780926, 'lng': 90.422858},
            },
            format='json',
        )

        self.assertEqual(response.status_code, 406)

    def test_search_location(self):
        client.force_authenticate(self.manager1)
        response = client.get(
            location_prefix + LOC_URLS['search_locations_map'],
            {
                'token': 'azimpur'
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print(response.data)

    def test_batch_upload_location(self):
        task1 = create_task('Task2', self.manager1, [self.agent11], status=TSTATE['In progress'])

        self.agent12.is_present = True
        self.agent12.save()

        client.force_authenticate(user=None)
        client.force_authenticate(self.agent11)
        # print('Uploading batch....')
        response = client.post(
            location_prefix + LOC_URLS['batch_upload_location'],
            {
                'mac': '00:0a:95:9d:68:16',
                'points': [
                    {
                        'timestamp': '2018-12-03 16:28:48.464495',
                        'point': {'lat': 23.780926, 'lng': 90.422858},
                        'event': 8
                    },
                    {
                        'timestamp': '2018-12-03 16:28:48.464495',
                        'point': {'lat': 23.780926, 'lng': 90.422858},
                        'event': 8
                    },
                ]
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        client.force_authenticate(user=None)
        client.force_authenticate(user=self.manager1)
        response = client.get(
            location_prefix + LOC_URLS['get_resource_history'],
            {
                'agent_id': self.agent11.id,
                'date': '2018-12-03',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print(response.data)

        response = client.get(
            location_prefix + LOC_URLS['get_resource_locations'],
            {},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print(response.data)
