import boto3
from background_task import background
from django.utils import timezone
from django.conf import settings
from apps.billing.config import *
from apps.billing.models import Payment
from apps.user.auth_helpers import get_username
from .mailer import Email
from .config import PACKAGE_INFO


client = boto3.client(
    'ses',
    region_name=settings.AWS_SES_REGION_NAME,
    aws_access_key_id=settings.AWS_SES_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SES_SECRET_ACCESS_KEY
)


@background(schedule=2)
def send_payment_mail(username, oid, amount, purpose):

    ToAddresses = ['teamwork.support@dingi.live', 'farhad.ahmed@dingi.live']
    subject = "New Payment"
    data = """
        Organization: {0}\n
        Bill paid by user: {1}\n
        Amount : {2}\n
        Purpose: {3}\n
    """.format(oid, username, amount, purpose)

    response = client.send_email(
        Destination={
            'ToAddresses': ToAddresses,
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': data,
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject,
            },
        },
        Source=settings.SENDER_EMAIL,
    )


@background(schedule=2)
def send_payment_mail_v2(
        admin_email, admin_name, payment_id, org_name, purpose,
        package, data_history, qtty_label, qtty, bill_total
):
    subject = "New Payment"
    # to_addresses = [admin_email, 'sk.farhad.eee@gmail.com']
    if admin_email:
        to_addresses = [admin_email, 'teamwork.support@dingi.live']
    else:
        to_addresses = ['teamwork.support@dingi.live']
    email = Email(settings.SENDER_EMAIL, subject)
    bill_act = round(bill_total * .952, 2)
    vat = round(bill_total * .048, 2)
    context = {
        'admin_name': admin_name,
        'payment_id': payment_id,
        'org_name': org_name,
        'pay_date': str(timezone.datetime.today().date()),
        'purpose': purpose,
        'package': package,
        'data_history': data_history,
        'qtty_label': qtty_label,
        'qtty': qtty,
        'bill_act': bill_act,
        'vat': vat,
        'bill_total': bill_total
    }
    email.html('bill_invoice.html', context)
    email.send(to_addresses)


@background(schedule=2)
def send_log_mail(description, log_obj='None'):
    ToAddresses = ['farhad.ahmed@dingi.live']
    subject = "Log Info"
    data = """
        Description: {0}\n
        Log obj: {1}\n
    """.format(description, str(log_obj))

    response = client.send_email(
        Destination={
            'ToAddresses': ToAddresses,
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': data,
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject,
            },
        },
        Source=settings.SENDER_EMAIL,
    )


def set_bill_type(organizer, bill_type, amount, new_agents, extra_tasks):
    purpose = 'Unknown'
    if bill_type == 1:
        organizer.org.subscription.renew_subscription(amount)
        purpose = 'New Subscription'
    if bill_type == 2:
        organizer.org.subscription.add_new_agents(new_agents, amount)
        purpose = 'Purchased new accounts. Quantity: {}'.format(new_agents)
    if bill_type == 3:
        organizer.org.subscription.add_extra_tasks(extra_tasks, amount)
        purpose = 'Purchased extra tasks. Quantity: {}'.format(extra_tasks)

    send_payment_mail(
        username=get_username(organizer),
        oid=organizer.org.oid,
        amount=amount,
        purpose=purpose
    )
    return purpose


def set_bill_type_v2(
        organizer, payment_uid, bill_type, amount, new_agents, extra_tasks
):
    sub = organizer.org.subscription
    admin_name = organizer.full_name
    admin_email = organizer.email
    org_name = organizer.org.org_name
    package = PACKAGE_INFO[sub.package]['title']
    data_history = '13 Months' if sub._is_premium else '13 Weeks'
    qtty_label = 'None'
    qtty = 'None'

    purpose = 'Unknown'
    if bill_type == 1:
        organizer.org.subscription.renew_subscription(amount)
        purpose = 'New Subscription'
        qtty_label = 'Total accounts'
        qtty = sub.agent_limit
    if bill_type == 2:
        organizer.org.subscription.add_new_agents(new_agents, amount)
        purpose = 'Purchased new accounts'
        qtty_label = 'New Accounts'
        qtty = new_agents
    if bill_type == 3:
        organizer.org.subscription.add_extra_tasks(extra_tasks, amount)
        purpose = 'Purchased extra tasks'
        qtty_label = 'Extra Tasks'
        qtty = extra_tasks

    send_payment_mail_v2(
        admin_email=admin_email,
        admin_name=admin_name,
        org_name=org_name,
        payment_id=payment_uid,
        purpose=purpose,
        package=package,
        data_history=data_history,
        qtty_label=qtty_label,
        qtty=qtty,
        bill_total=amount
    )
    return True


def update_subscription_bksah(serializer, organizer, payment_log):
    bill_type = int(serializer.data['bill_type'])
    amount = float(serializer.data['amount'])
    extra_tasks = int(serializer.data['extra_tasks'])
    new_agents = int(serializer.data['new_agents'])
    payment_uid = serializer.data['payment_uid']

    # set_bill_type(organizer, bill_type, amount, new_agents, extra_tasks)

    payment = Payment.objects.get(payment_uid=payment_uid)
    payment.details = payment_log
    payment.bill_type = bill_type
    payment.vendor_uid = payment_log['paymentID']
    payment.state = PAYMENT_STATUS_DICT['Successful']
    payment.save()

    try:
        set_bill_type_v2(
            organizer=organizer,
            payment_uid=payment_uid,
            bill_type=bill_type,
            amount=amount,
            new_agents=new_agents,
            extra_tasks=extra_tasks
        )
    except Exception as e:
        print('Payment failed! Error:' + str(e))


def update_subscription_ssl_web(ssl_data, organizer, payment_log):
    bill_type = int(ssl_data['bill_type'])
    amount = float(ssl_data['amount'])
    extra_tasks = int(ssl_data['extra_tasks'])
    new_agents = int(ssl_data['new_agents'])
    payment_uid = ssl_data['payment_uid']
    vendor_uid = ssl_data['val_id']

    # set_bill_type(organizer, bill_type, amount, new_agents, extra_tasks)

    payment = Payment.objects.get(payment_uid=payment_uid)
    payment.vendor_uid = vendor_uid
    payment.state = PAYMENT_STATUS_DICT['Successful']
    payment.details = payment_log
    payment.save()
    try:
        set_bill_type_v2(
            organizer=organizer,
            payment_uid=payment_uid,
            bill_type=bill_type,
            amount=amount,
            new_agents=new_agents,
            extra_tasks=extra_tasks
        )
    except Exception as e:
        print('Payment failed! Error:' + str(e))


def update_subscription_ssl(serializer, organizer, payment_log):
    bill_type = int(serializer.data['bill_type'])
    amount = float(serializer.data['amount'])
    extra_tasks = int(serializer.data['extra_tasks'])
    new_agents = int(serializer.data['new_agents'])

    set_bill_type(organizer, bill_type, amount, new_agents, extra_tasks)

    payment = serializer.create(serializer.validated_data)
    payment.subscription = organizer.org.subscription
    payment.details = payment_log
    payment.state = PAYMENT_STATUS_DICT['Successful']
    payment.save()
