from .config import *
from .helpers import *


# User notifications
def attendance_notification(user, presence):
    if presence:
        status_text = 'online!'
    else:
        status_text = 'offline!'
    text = 'Employee ' + user.full_name + \
           ' just went ' + status_text
    notification = Notification(
        type=NTD['Alert'],
        title='Alert',
        agent=user,
        recipient=user.parent,
        text=text,
    )
    notification.save()
    resp = send_notification(notification)
    # print(resp)
    return resp


def unreachable_notification(user):
    text = 'Employee ' + user.full_name + \
           ' just became unreachable!'
    notification = Notification(
        type=NTD['Unreachable'],
        title='Unreachable',
        agent=user,
        recipient=user.parent,
        text=text,
    )
    notification.save()
    resp = send_notification(notification)
    # print(resp)
    return resp


def force_offline_notification(user):
    text = 'You were sent offline by system! Go online again to continue working.'
    notification = Notification.objects.create(
        type=NTD['Force Offline'],
        title='Force Offline',
        agent=user,
        recipient=user,
        text=text
    )
    resp = send_notification(notification)
    # print(resp)
    return resp


# Task Notification
def new_task_notification(task):
    recipients = []
    resps = []
    for agent in task.agent_list.all():
        recipients.append(agent)
    manager = task.manager
    text = 'New task: ' + task.title + ' just created by ' + manager.full_name

    for rcpt in recipients:
        notification = Notification.objects.create(
            type=NTD['New Task'],
            title='New Task',
            task=task,
            text=text,
            recipient=rcpt
        )
        resps.append(send_notification(notification))
    return resps


def task_delayed_notification(task):
    recipients = []
    resps = []
    manager = task.manager
    recipients.append(manager)
    for agent in task.agent_list.all():
        recipients.append(agent)
    text = 'Deadline crossed for ' + task.title

    for rcpt in recipients:
        notification = Notification.objects.create(
            type=NTD['Deadline crossed'],
            title='Deadline crossed',
            text=text,
            task=task,
            recipient=rcpt
        )
        resps.append(send_notification(notification))
    return resps


def task_change_notification(user, task, change_type):
    recipients = []
    resps = []
    manager = task.manager
    recipients.append(manager)
    for agent in task.agent_list.all():
        recipients.append(agent)

    text = 'Task: ' + task.title + \
           ' just ' + NTC[change_type][1].replace('Task', '') + \
           ' by ' + user.full_name

    for rcpt in recipients:
        notification = Notification.objects.create(
            type=change_type,
            title=get_ntf_title(change_type),
            task=task,
            recipient=rcpt,
            text=text
        )
        resps.append(send_notification(notification))

    return resps


# Assignment notifications
def get_recipients(assignment, issuer):
    recipients = [
        assignment.creator,
        assignment.manager
    ]
    for user in assignment.assignee_list.all():
        recipients.append(user)
    if assignment.assignee:
        recipients.append(assignment.assignee)

    if issuer in recipients:
        recipients.remove(issuer)
    return recipients


def assignment_notification(assignment, ntf_type, issuer, text=''):
    resps = []
    recipients = get_recipients(assignment, issuer)

    ntf_title = get_ntf_title(ntf_type)

    for rcpt in recipients:
        if rcpt:
            notification = Notification.objects.create(
                type=ntf_type,
                title=ntf_title,
                agent=issuer,
                recipient=rcpt,
                assignment=assignment,
                text=text
            )
            resps.append(send_notification(notification))
    # print(resp)
    return resps


def ping_device(user, ntf_type):
    try:
        text = 'Pinging user: ' + user.full_name
        notification = Notification(
            type=NTD['Ping Device'],
            title='Ping Device',
            agent=user,
            recipient=user,
            text=text,
        )
        notification.save()

        message = messaging.Message(
            data={
                'type': 'notification',
                'notification_type': str(ntf_type),
                'title': 'Ping',
                'body': 'Pinging device for location update!'
            },
            token=user.fb_token,
        )
        resp = messaging.send(message)
    except Exception as e:
        resp = str(e)
    return resp


