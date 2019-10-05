from django.test import TestCase
import uuid
# from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.user.helpers import create_agent, create_manager, create_organizer
from apps.billing.urls import BILL_URLS
from apps.billing.models import Payment, Usage, Subscription
from apps.billing.config import FREE_AGENT, FREE_TASK


User = get_user_model()
client = APIClient()

billing_prefix = '/v0/billing/'


class BillingTestCase(TestCase):

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

    def test_get_usage(self):
        # print('Testing renew subscription')
        client.force_authenticate(self.manager1)

        response = client.get(
            billing_prefix + BILL_URLS['get_usage'],
            {},
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reseller_info(self):
        # print('Testing renew subscription')
        client.force_authenticate(self.manager1)

        response = client.get(
            billing_prefix + BILL_URLS['get_usage'],
            {},
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reseller'], None)

        self.manager1.org.has_reseller = True
        self.manager1.org.reseller_name = 'Grameenphone'
        self.manager1.org.reseller_panel_link = 'www.gpcloud.com'
        self.manager1.org.save()
        response = client.get(
            billing_prefix + BILL_URLS['get_usage'],
            {},
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reseller']['company'], 'Grameenphone')

    def test_renew_subscription(self):
        # print('Testing renew subscription')
        client.force_authenticate(self.manager1)
        usage = self.manager1.org.subscription.current_usage
        usage.status = 2
        usage.save()

        response = client.get(
            billing_prefix + BILL_URLS['get_usage'],
            {},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], False)

        self.manager1.org.subscription.renew_subscription(100.0)

        response = client.get(
            billing_prefix + BILL_URLS['get_usage'],
            {},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], True)

    def test_extra_tasks(self):
        # print('Testing extra tasks')
        manager1 = self.manager1
        cur_usage = self.manager1.org.subscription.current_usage

        client.force_authenticate(manager1)
        response = client.get(
            billing_prefix + BILL_URLS['get_usage'],
            {},
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        extra_task = 20
        amount = 10
        manager1.org.subscription.add_extra_tasks(extra_task, amount)

        response = client.get(
            billing_prefix + BILL_URLS['get_usage'],
            {},
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cur_usage.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task_limit'], FREE_TASK + extra_task)
        self.assertEqual(cur_usage.bill_extra_task, amount)

    def test_new_agents(self):
        # print('Testing extra tasks')
        manager1 = self.manager1
        cur_usage = self.manager1.org.subscription.current_usage

        client.force_authenticate(manager1)
        response = client.get(
            billing_prefix + BILL_URLS['get_usage'],
            {},
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_agent = 5
        amount = 100
        manager1.org.subscription.add_new_agents(new_agent, amount)

        response = client.get(
            billing_prefix + BILL_URLS['get_usage'],
            {},
            format='json',
        )
        # print(response.data)
        cur_usage.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['available_accounts'], FREE_AGENT + new_agent)
        self.assertEqual(cur_usage.bill_new_agent, amount)

    def test_set_package(self):
        organizer1 = self.organizer1
        client.force_authenticate(organizer1)
        response = client.post(
            billing_prefix + BILL_URLS['set_package'],
            {
                'user_id': organizer1.id,
                'is_premium': True,
                'package_id': 4,
            },
            format='json',
        )
        # print(response.data)
        # print(organizer1.org.subscription.package)
        organizer1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(organizer1.org.subscription.package, 4)

    def test_bkash_execute_payment(self):

        payment_uid = str(uuid.uuid4())
        payment = Payment(
            payment_uid=payment_uid,
            vendor_uid=payment_uid,
            subscription=self.organizer1.org.subscription,
            amount=100,
            package=self.organizer1.org.subscription.package,
        )
        payment.save()

        organizer1 = self.organizer1
        client.force_authenticate(organizer1)
        response = client.post(
            billing_prefix + BILL_URLS['execute_payment'],
            {
                "gateway": 1,
                "vendor_uid": 'M9JVAIM1565090515431',
                "payment_uid": payment_uid,
                "bill_type": 1,
                "amount": '240.0',
                "extra_tasks": 0,
                "new_agents": 0
            },
            format='json',
        )
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO: remove after test
    #
    # def test_mailer(self):
    #
    #     organizer1 = self.organizer1
    #     client.force_authenticate(organizer1)
    #     response = client.post(
    #         billing_prefix + BILL_URLS['send_mail'],
    #         {
    #         },
    #         format='json',
    #     )
    #     print(response.data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
