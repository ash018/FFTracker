from django.utils import timezone
import uuid
from apps.billing.models import Subscription, Payment
from apps.billing.serializers import BkashPaymentSerializer
from django.db.models import Q, F
from apps.user.models import User
from apps.user.config import ROLE_DICT
from django.shortcuts import render
from apps.billing.models import Subscription

import requests
from apps.billing.config import *


def get_sub(request):
    sub_qs = Subscription.objects.filter(
        Q(org=request.user.org)
    ).select_related('current_usage')
    # print(sub_qs.query)
    return sub_qs[0]


def check_subscription(request):
    try:
        subs = get_sub(request)
        return subs.current_usage.status == USAGE_DICT['active']
    except Exception as e:
        print(str(e))
        return True


def adjust_subscription(request):
    try:
        subs = get_sub(request)
        if subs.current_usage.exp_date < timezone.now():
            subs.current_usage.status = USAGE_DICT['expired']
            subs.current_usage.save()
    except Exception as e:
        print(str(e))
        return True


def check_task_quantity(request, tasks):
    try:
        subs = get_sub(request)
        status = subs.current_usage.status
        consumed_tasks = subs.current_usage.consumed_tasks + tasks
        if status != USAGE_DICT['active'] or consumed_tasks > subs.task_limit:
            return False
        return True
    except Exception as e:
        print(str(e))
        return True


def check_user_count(request):
    try:
        subs = get_sub(request)
        status = subs.current_usage.status
        if status != USAGE_DICT['active'] or subs.added_agents >= subs.agent_limit:
            return False
        return True
    except Exception as e:
        print(str(e))
        return True


def adjust_user_count(request):
    organizer = request.user
    try:
        subs = get_sub(request)
        subs.added_agents = User.objects.filter(
            Q(org=organizer.org) &
            Q(role__in=[ROLE_DICT['Manager'], ROLE_DICT['Employee']])
        ).count()
        subs.save()
    except Exception as e:
        print(str(e))


def adjust_task_quantity(request, instances):
    try:
        subs = get_sub(request)
        subs.current_usage.consumed_tasks = F('consumed_tasks') + instances
        subs.current_usage.save()
    except Exception as e:
        print(str(e))


def get_token():
    url = BKASH_CONF["live_checkout_url"] + "/token/grant"
    headers = {
        "username": BKASH_CONF["headers"]["username"],
        "password": BKASH_CONF["headers"]["password"]
    }
    payload = {
        'app_key': BKASH_CONF["body"]["app_key"],
        'app_secret': BKASH_CONF["body"]["app_secret"]
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def create_payment_bkash(token, amount, intent):
    url = BKASH_CONF["live_checkout_url"] + "/payment/create"
    payload = {
        "amount": amount,
        "currency": "BDT",
        "intent": intent,
        "merchantInvoiceNumber": "12124567"
    }
    headers = {
        "authorization": token,
        "x-app-key": BKASH_CONF["body"]["app_key"]
    }
    response = requests.post(url, json=payload, headers=headers)
    # print(response.text)
    return response.json()


def validate_payment_create_bkash(payment_uid, user, bill_type):
    if not payment_uid:
        return False
    payment_qs = Payment.objects.filter(
        Q(payment_uid=payment_uid) &
        Q(state=PAYMENT_STATUS_DICT['Initiated']) &
        Q(subscription=user.org.subscription)
    )
    if len(payment_qs) < 1:
        return False
    payment = payment_qs.order_by('-timestamp')[0]
    payment.state = PAYMENT_STATUS_DICT['Created']
    payment.bill_type = int(bill_type)
    payment.save()
    return True


def execute_payment_bkash(token, paymentID):
    url = BKASH_CONF["live_checkout_url"] + "/payment/execute/" + paymentID
    headers = {
        'authorization': token,
        'x-app-key': BKASH_CONF["body"]["app_key"]
    }
    response = requests.post(url, headers=headers)
    return response.json()


def create_payment_ssl(validated_data, organizer):

    """
    const data  = JSON.stringify({
        store_id: config["SSL_STORE_ID"],
        store_passwd: config["SSL_STORE_PASSWORD"],
        total_amount: amount,
        currency: 'BDT',
        tran_id: uniqid(),
        success_url: config["SSL_SUCCESS_URL"],
        fail_url: config["SSL_FAILED_URL"],
        cancel_url: config["SSL_CANCEL_URL"],
        cus_name: cusName,
        cus_email: cusEmail,
        cus_phone: cusPhone,
        value_a: `${amount}<#>${billType}<#>${extraAgents}<#>${extraTasks}<#>${cusPhone}`
    });

    const res = await axios.get(`https://${config["SSL_PAYMENT_MODE"]}.sslcommerz.com/gwprocess/v3/api.php`, data ,{
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
    });
    """
    # print('Inside create method...')
    # print(validated_data)

    amount = str(validated_data['amount'])
    bill_type = str(validated_data['bill_type'])
    new_agents = str(validated_data['new_agents'])
    extra_tasks = str(validated_data['extra_tasks'])
    payment_uid = str(uuid.uuid4())

    payment = Payment.objects.create(
        gateway=2,
        vendor_uid=payment_uid,
        payment_uid=payment_uid,
        amount=amount,
        bill_type=bill_type,
        extra_tasks=extra_tasks,
        new_agents=new_agents,
        subscription=organizer.org.subscription
    )

    value_a = amount + '<#>' + bill_type + '<#>' + \
              new_agents + '<#>' + extra_tasks + '<#>' + \
              organizer.username + '<#>' + payment_uid

    url = SSL_CONF["secure_create_url_ssl"]
    payload = {
        'store_id': SSL_CONF['store_id'],
        'store_passwd': SSL_CONF['store_passwd'],
        'total_amount': float(amount),

        'currency': 'BDT',
        'tran_id': str(uuid.uuid4()),
        'success_url': SSL_REDIRECT_URL,
        'fail_url': SSL_REDIRECT_URL,
        'cancel_url': SSL_REDIRECT_URL,
        'cus_name': organizer.full_name,
        'cus_email': organizer.email,
        'cus_phone': organizer.phone,
        'value_a': value_a,


    }
    response = requests.post(url, data=payload)
    # print(response.json())
    return response.json()


def validate_payment_ssl(val_id):
    url = SSL_CONF["secure_validator_url_ssl"]
    params = {
        "val_id": val_id,
        'store_id': SSL_CONF['store_id'],
        'store_passwd': SSL_CONF['store_passwd'],
    }

    # params = {
    #     "val_id": val_id,
    #     'store_id': SSL_CONF['sandbox_store_id'],
    #     'store_passwd': SSL_CONF['sandbox_store_passwd'],
    # }
    response = requests.get(url, params=params)
    return response.json()


def render_context(request, template, context, status):
    return render(request, template, {'context': context}, status=status)


def get_url(request, prefix, uri):
    url = request.build_absolute_uri().replace(
        'bkash/template/', prefix + BILL_URLS[uri]
    )
    return url


def get_user(request):
    if not request.user.is_authenticated:
        return {
            'id': -1,
            'name': 'Anonymous',
            'phone': ''
        }
    user = request.user

    return {
        'id': user.id,
        'phone': user.phone,
        'name': user.full_name,
    }


def get_context(request):

    context = {
        'user': get_user(request),
        'bkash_template': get_url(request, '', 'bkash_template'),
        'bkash_success_template': get_url(request, '', 'bkash_success_template').split('?', 1)[0],
        'bkash_fail_template': get_url(request, '', 'bkash_fail_template').split('?', 1)[0],
        'create_payment': get_url(request, '', 'create_payment').split('?', 1)[0],
        'execute_payment': get_url(request, '', 'execute_payment').split('?', 1)[0],


    }
    return context


