from django.db import transaction
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.user.permissions import is_organizer
from apps.user.helpers import get_active_accounts
from .helpers import *
from .payment_executors import update_subscription_bksah, \
    update_subscription_ssl, update_subscription_ssl_web
from .serializers import BkashPaymentSerializer, SSLCreateSerializer, \
    SSLExecuteSerializer

from .mailer import Email

# from .payment_executors import send_log_mail


def get_unit_price(package, is_premium):
    return PACKAGE_INFO[package]['price'] + PREMIUM_STORAGE \
               if is_premium else PACKAGE_INFO[package]['price'],


class GetAppUsage(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
         Sample Response:
         ---

             {
                'available_accounts': 25,
                'added_agents': 15,
                'active_agents': 10,
                'task_limit': 1000,
                'consumed_tasks': 500,
                'expires': '12-12-12 12:12:1212',
                'status': true,
                'reseller':{
                    'company': 'Grameenphone',
                    'billing_url': 'url...'
                }
             }


        """
        # is_organizer(request)
        organizer = request.user
        sub = organizer.org.subscription
        usage = {
            'available_accounts': sub.agent_limit,
            'active_agents': get_active_accounts(organizer),
            'added_agents': sub.added_agents,
            'task_limit': sub.task_limit,
            'consumed_tasks': sub.current_usage.consumed_tasks,
            'expires': str(sub.current_usage.exp_date),
            'status': sub.current_usage.status == 1,
            'reseller': {
                'company': organizer.org.reseller_name,
                'billing_url': organizer.org.reseller_panel_link,
            } if organizer.org.has_reseller else None,
        }

        return Response(usage, status=200)


class NewSubscriptionBill(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Parameter details:
        ---
            promo_code:
                type: str
                required: No
        Sample response:
        ---

             {
                'bill': 900.00,
                'is_organizer': true,
                'unit_price': 180,
                'added_agents': 5,
                'is_organizer': true,
             }

        """
        # is_organizer(request)
        organizer = request.user
        sub = organizer.org.subscription

        promo_code = request.query_params.get('promo_code', False)
        bill = sub.new_subscription_bill(promo_code)
        is_premium = sub._is_premium
        recent_package = sub.package
        msg = {
            'bill': bill,
            'is_premium': is_premium,
            'unit_price': get_unit_price(recent_package, is_premium),
            'added_agents': sub.added_agents,
            'is_organizer': organizer.role == ROLE_DICT['Organizer'],
        }
        return Response(msg, status=200)


class NewAgentsBill(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Parameter details:
        ---
            new_agents:
                type: int
                required: yes
            promo_code:
                type: str
                required: No
        Sample response:
        ---

             {
                'bill': 900.00,
                'is_organizer': true,
                'is_premium': true,
                'unit_price': 180,
                'new_agents': 5,
             }

        """
        # is_organizer(request)
        organizer = request.user
        sub = organizer.org.subscription

        if sub.renew_needed:
            msg = 'Package was upgraded recently. Please renew subscription!'
            return Response({'detail': msg}, status=406)

        new_agents = int(request.query_params.get('new_agents', False))
        if not new_agents:
            return Response({'msg': 'Provide agent quantity!'}, status=200)
        promo_code = request.query_params.get('promo_code', False)
        bill = sub.new_agent_bill(new_agents, promo_code)
        is_premium = sub._is_premium
        package = sub.current_usage.package
        msg = {
            'bill': bill,
            'is_organizer': organizer.role == ROLE_DICT['Organizer'],
            'is_premium': is_premium,
            'unit_price': get_unit_price(package, is_premium),
            'new_agents': new_agents,
        }
        return Response(msg, status=200)


class ExtraTasksBill(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Parameter details:
        ---
            extra_tasks:
                type: int
                required: yes
            promo_code:
                type: str
                required: No
        Sample response:
        ---

            {
                'bill': 50.00,
                'is_organizer': true,
                'is_premium': is_premium,
                'unit_price': 0.5,
                'extra_tasks': 100
            }

        """
        # is_organizer(request)
        organizer = request.user
        sub = organizer.org.subscription

        if sub.renew_needed:
            msg = 'Package was upgraded recently. Please renew subscription!'
            return Response({'detail': msg}, status=406)

        extra_tasks = int(request.query_params.get('extra_tasks', False))
        if not extra_tasks:
            return Response({'detail': 'Provide task quantity!'}, status=400)
        promo_code = request.query_params.get('promo_code', False)
        bill = sub.new_task_bill(extra_tasks, promo_code)
        is_premium = sub._is_premium
        msg = {
            'bill': bill,
            'is_organizer': organizer.role == ROLE_DICT['Organizer'],
            'is_premium': is_premium,
            'unit_price': EXTRA_TASK_PRICE,
            'extra_tasks': extra_tasks
        }
        return Response(msg, status=200)


class PackageViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request, format=None):
        """
        Sample submit:
        ---
            {
                'user_id': 23,
                'is_premium': true,
                'package_id': 2,
            }

        """
        # TODO: Prevent updates through this
        is_organizer(request)
        user_id = request.data.get('user_id', False)
        if not user_id:
            return Response({'detail': 'Provide user id!'}, status=400)
        organizer = User.objects.get(id=user_id)
        is_premium = bool(request.data.get('is_premium', False))
        package_id = int(request.data.get('package_id', 3))
        sub = organizer.org.subscription
        cur_usage = sub.current_usage
        sub._is_premium = is_premium
        sub.package = package_id
        sub.save()
        cur_usage.package = package_id
        cur_usage.save()
        return Response({'msg': 'OK'}, status=201)

    def update(self, request, pk, format=None):
        """
        Sample submit:
        ---
            {
                'is_premium': true,
                'package_id': 2,
            }

        """
        is_organizer(request)
        organizer = User.objects.get(id=pk)
        is_premium = bool(request.data.get('is_premium', False))
        package_id = int(request.data.get('package_id', 3))
        organizer.org.subscription._is_premium = is_premium
        if organizer.org.subscription.package != package_id:
            organizer.org.subscription.package = package_id
            organizer.org.subscription.renew_needed = True
        organizer.org.subscription.save()
        return Response({'msg': 'OK'}, status=200)

    def retrieve(self, request, pk, format=None):
        """
        Sample response:
        ---
            {
                'is_premium': true,
                'package_id': 2,
                'package_details': {
                    'price': 100,
                    'has_attendance': True,
                    'has_agent_tracking': True,
                    'has_messaging': True,
                    'has_task_management': False,
                }
            }

        """
        is_organizer(request)
        organizer = User.objects.get(id=pk)
        data = {
            'package_id': organizer.org.subscription.package,
            'package_details': PACKAGE_INFO[organizer.org.subscription.package],
            'is_premium': organizer.org.subscription._is_premium,
            'renew_needed': organizer.org.subscription.renew_needed,
        }
        return Response(data, status=200)


class CreatePaymentInternal(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Sample Submit:
        ---
            {
                'amount': 200.0,
                'bill_type': 1
            }

        Sample Response:
        ---
            {
                'payment_uid': '23gi-ugig-u4g4-849y4..',
                'amount': 200.0,
            }
        """
        user = request.user
        # print('Creating payment internal.............')
        # print(request.data)
        amount = request.data.get('amount', False)
        bill_type = request.data.get('bill_type', 1)
        if not amount:
            data = {
                'msg': 'Provide amount!',
            }
            return Response(data, status=400)

        payment_qs = Payment.objects.filter(Q(subscription=user.org.subscription))
        if len(payment_qs) > 0:
            last_payment = payment_qs.order_by('-timestamp')[0]
            min_diff = timezone.timedelta(seconds=5)
            if (timezone.now() - last_payment.timestamp) < min_diff:
                data = {
                    'msg': 'Please wait 5 more seconds!',
                }
                return Response(data, status=406)

        payment_uid = str(uuid.uuid4())
        payment = Payment(
            payment_uid=payment_uid,
            vendor_uid=payment_uid,
            bill_type=bill_type,
            subscription=user.org.subscription,
            amount=float(amount),
            package=user.org.subscription.package,
        )
        payment.save()

        data = {
            'msg': 'successful',
            'payment_uid': payment_uid,
            'amount': amount
        }
        return Response(data, status=200)


class CreatePaymentBkash(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        # print('Creating payment bkash.............')
        # print(request.data)
        user = request.user
        token = get_token()['id_token']
        amount = request.data.get('amount', False)
        bill_type = request.data.get('bill_type', 1)
        intent = request.data.get('intent', False)
        payment_uid = request.data.get('payment_uid', False)

        if not validate_payment_create_bkash(payment_uid, user, bill_type):
            # print('Invalid payment.....')
            msg = {
                "errorCode": "7001",
                "errorMessage": "Invalid Payment Creation"
            }
            return Response(msg, status=400)

        payment_log = create_payment_bkash(token, amount, intent)
        # send_log_mail('Testing email with Bkash payment log', payment_log)
        # print(payment_log)
        return Response(payment_log, status=200)


class ExecutePaymentBkash(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Sample submit:
        ---
            {
                "gateway": 1,
                "vendor_uid": '0GL0BVI1543309772718',
                "payment_uid": 'a132-4dfk-asjdf-hakshd',
                "bill_type": 1,
                "amount": '780.0',
                "extra_tasks": 0,
                "new_agents": 0
            }

        """

        serializer = BkashPaymentSerializer(data=request.data)
        # print(serializer.initial_data)
        if serializer.is_valid():
            # print('Executing bkash payment.............')
            # print(request.data)
            is_organizer(request)
            paymentID = serializer.data['vendor_uid']
            token = get_token()["id_token"]
            organizer = request.user
            payment_log = execute_payment_bkash(token, paymentID)

            '''
            SUCCESS:
            {
              "paymentID": "3FGA3YC1543309140580",
              "createTime": "2018-11-27T08:59:00:660 GMT+0000",
              "updateTime": "2018-11-27T08:59:30:017 GMT+0000",
              "trxID": "5KR201949E",
              "transactionStatus": "Completed",
              "amount": "100.50",
              "currency": "BDT",
              "intent": "sale",
              "merchantInvoiceNumber": "12124567"
            }
            
            ERROR:
            {
                'errorCode': '2023', 
                'errorMessage': 'Insufficient Balance'
            }
            '''
            # send_log_mail('Bkash payment log', payment_log)
            try:
                if payment_log['transactionStatus'] == 'Completed':
                    with transaction.atomic():
                        update_subscription_bksah(serializer, organizer, payment_log)
                    return Response({'msg': 'Payment Successful!'}, status=200)
                return Response(payment_log, status=402)
            except Exception as e:
                return Response(payment_log, status=400)
        else:
            # print(serializer.errors)
            return Response(serializer.errors, status=400)


class BkashPaymentTemplate(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Query Parameter details:
        ---
            bill_type:
                type: int
                required: Yes
                choices: (1, new subscription), (2, new agents), (3, extra tasks)
            amount:
                type: float
                required: Yes
            new_agents:
                type: int
                default: 0
            extra_tasks:
                type: int
                default: 0
            payment_uid:
                type: str
                required: Yes

        Response:
        ---
             Bkash HTML page..
        """
        is_organizer(request)
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        bill_type = request.query_params.get('bill_type', False)
        amount = request.query_params.get('amount', False)
        extra_tasks = request.query_params.get('extra_tasks', 0)
        new_agents = request.query_params.get('new_agents', 0)
        payment_uid = request.query_params.get('payment_uid', 'None')

        if (not amount) or (not bill_type):
            return render_context(request, 'billing/payment_error.html', {}, 400)

        context = get_context(request)
        context.update({
            'bill_type': bill_type,
            'amount': amount,
            'extra_tasks': extra_tasks,
            'new_agents': new_agents,
            'token': token,
            'payment_uid': payment_uid,
        })

        # print(context)
        return render_context(request, 'billing/bkash.html', context, 200)


class BkashPaymentErrorPage(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, format=None):
        msg = request.query_params.get('msg', 'None')
        # print('Bkash error: ' + msg)
        return render_context(request, 'billing/payment_error.html', {}, 200)


class BkashPaymentSuccessPage(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, format=None):
        return render_context(request, 'billing/payment_success.html', {}, 200)


class CreatePaymentSSL(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        """
        Sample Submit:
        ---
            {
                'gateway': 2,
                'amount': 2,
                'bill_type': 1,
                'extra_tasks': 3,
                'new_agents':3
            }
        """
        serializer = SSLCreateSerializer(data=request.data)
        organizer = request.user

        is_organizer(request)
        if serializer.is_valid():
            # print('Creating payment SSL.............')
            payment_log = create_payment_ssl(serializer.data, organizer)
            # print(payment_log)

            return Response(payment_log, status=200)
        else:
            return Response(serializer.errors, status=400)


@csrf_exempt
def ssl_redirect(request):
    # print(request.POST)
    value_a = request.POST.get('value_a', False)
    val_id = request.POST.get('val_id', False)
    amount, bill_type, new_agents, extra_tasks, username, payment_uid = value_a.split('<#>')
    ssl_data = {
        'gateway': 2,
        'bill_type': bill_type,
        'amount': amount,
        'new_agents': new_agents,
        'extra_tasks': extra_tasks,
        'val_id': val_id,
        'payment_uid': payment_uid
    }

    organizer = User.objects.get(username=username)
    # if not organizer.is_organizer:
    #     context = {
    #         'status': 'failed',
    #         'msg': 'Please contact organization admin for payment!'
    #     }
    #     return render(request, 'billing/ssl_redirect.html', context, 200)

    if not Payment.objects.filter(Q(payment_uid=payment_uid)).exists():
        context = {
            'status': 'fail',
            'msg': 'This payment instance is invalid!'
        }
        return render(request, 'billing/ssl_redirect.html', context, 200)

    payment_log = validate_payment_ssl(val_id)

    # send_log_mail('SSL payment log', payment_log)
    if payment_log['status'] in ['VALIDATED', 'VALID']:
        update_subscription_ssl_web(ssl_data, organizer, payment_log)
        context = {
            'status': 'success',
            'msg': ''
        }
    else:
        context = {
            'status': 'failed',
            'msg': 'Invalid credentials!'
        }

    return render(request, 'billing/ssl_redirect.html', context, 200)


class ExecutePaymentSSL(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        """
        Sample Submit:
        ---
            {
                "gateway": 2,
                "vendor_uid": '1812101604200QyijFyMPMMBNtK', ('val_id' from SSL)
                "bill_type": 1,
                "amount": '780.0',
                "extra_tasks": 0,
                "new_agents": 0
            }
        """
        serializer = SSLExecuteSerializer(data=request.data)
        if serializer.is_valid():
            # print(serializer.data)
            val_id = serializer.data['vendor_uid']
            payment_log = validate_payment_ssl(val_id)

            if Payment.objects.filter(Q(vendor_uid=val_id)).exists():
                msg = 'This payment is expired!'
                return Response({'msg': msg}, status=400)

            # print('Executing payment SSL.............')
            # print(payment_log)
            is_organizer(request)
            organizer = request.user
            if payment_log['status'] == 'VALIDATED':
                update_subscription_ssl(serializer, organizer, payment_log)
                return Response({'msg': 'OK'}, status=200)
            msg = 'Payment is invalid!'
            return Response({'msg': msg}, status=400)
        else:
            return Response(serializer.errors, status=400)


class SendMail(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        # TODO: Remove after mail testing
        email = Email('no-reply@dingi.live', 'test')
        bill_total = 1980
        bill_act = round(bill_total * .952, 2)
        vat = round(bill_total * .048, 2)
        bill_total = bill_act + vat
        context = {
            'admin_name': 'Admin',
            'payment_id': '1234-aeee-aefa-aeaa-aeaf-aefese',
            'org_name': 'Dingi',
            'pay_date': str(timezone.datetime.today().date()),
            'purpose': 'New Subscription',
            'package': 'Full Suit',
            'data_history': '13 weeks',
            'qtty_label': 'Total accounts',
            'qtty': 13,
            'bill_act': bill_act,
            'vat': vat,
            'bill_total': bill_total
        }
        email.html('bill_invoice.html', context)
        try:
            email.send(['farhad.ahmed@dingi.live', 'sk.farhad.eee@gmail.com'])
            return Response({'msg': 'OK'}, status=200)
        except Exception as e:
            return Response({'msg': str(e)}, status=400)

