import datetime as DT
from django.db.models import Q
from django.utils import timezone

from apps.user.models import User, DataUsage
from apps.user.config import ROLE_DICT
from apps.user.auth_helpers import create_username, get_username
from apps.org.models import Organization
from apps.billing.models import Usage, Subscription
from apps.task.models import Task
from apps.task.config import TASK_STATUS_DICT as TSTATE
from apps.message.models import Thread


from apps.state.models import UserState


def get_active_accounts(organizer):
    agent_count = User.objects.filter(
        Q(org=organizer.org) & Q(is_active=True) &
        Q(role__in=[ROLE_DICT['Manager'], ROLE_DICT['Employee']])
    ).count()
    return agent_count


def get_current_task(user):
    cur_tasks = Task.objects.filter(
        Q(status=TSTATE['In progress']) &
        Q(agent_list=user)
    )
    task_list = []
    for task in cur_tasks:
        task_details = {
            'title': task.title,
            'status': task.status,
            'start': task.start,
            'deadline': task.deadline,
            'task_type': task.task_type,
            'address': task.address,
            'id': task.id,
        }
        task_list.append(task_details)
    return task_list


def delete_agent_data(user):

    tasks = Task.objects.filter(Q(agent_list=user))
    for task in tasks:
        if task.status == TSTATE['In progress']:
            task.status = TSTATE['Cancelled']
        task.agent_list.remove(user)
        task.save()

    threads = Thread.objects.filter(Q(members=user))
    for thread in threads:
        thread.members.remove(user)
        thread.save()
    try:
        user.userstate.delete()
        user.delete()
    except Exception as e:
        print('Error in deleting user data: ' + str(e))
    return True


def delete_manager_data(user):
    msg_grps = Thread.objects.filter(Q(members=user))
    for grp in msg_grps:
        grp.delete()

    try:
        user.userstate.delete()
        user.delete()
    except Exception as e:
        print('Error in deleting user data: ' + str(e))
    return True


def create_org(oid):
    org = Organization(oid=oid)
    org.save()
    usage = Usage(
        org=org,
        package=3
    )
    usage.save()
    subscription = Subscription(org=org, current_usage=usage)
    subscription.save()
    return org


def create_organizer(username, oid='org1'):
    org = create_org(oid)

    organizer = User(
        username=create_username(oid, username), is_active=True,
        role=ROLE_DICT['Organizer'],
        org=org,
        full_name='Organizer',
    )
    organizer.set_unusable_password()
    organizer.save()
    state = UserState.objects.create(user=organizer)
    return organizer


def create_manager(username, parent, org):
    manager = User(
        username=create_username(org.oid, username), is_active=True,
        role=ROLE_DICT['Manager'],
        org=org,
        parent=parent,
        full_name='Manager',
    )

    manager.set_unusable_password()
    manager.save()
    manager.org.subscription.added_agents += 1
    manager.org.subscription.save()
    state = UserState.objects.create(user=manager)
    return manager


def create_agent(username, parent, is_present=True):
    oid = parent.org.oid
    org = parent.org
    agent = User(
        username=create_username(oid, username), is_active=True,
        org=org, role=ROLE_DICT['Employee'], parent=parent,
        is_present=is_present,
        full_name='Agent',
    )
    agent.set_unusable_password()
    agent.save()
    org.subscription.added_agents += 1
    org.subscription.save()
    state = UserState.objects.create(user=agent)
    return agent
