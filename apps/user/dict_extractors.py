from apps.billing.config import PACKAGE_INFO
from apps.common.task_templates import get_other_templates, TASK_TYPE, DOMAIN_CONF
from apps.user.auth_helpers import get_username
from apps.user.config import ROLE_DICT
from apps.common.models import AppInfo


def get_user_list(user_obj_list):
    user_details_list = []
    for user in user_obj_list:
        user_details = get_user_details(user)
        user_details_list.append(user_details)
    return user_details_list


def get_user_details(user):
    return {
        'id': user.id,
        'username': get_username(user),
        'email': user.email,
        'full_name': user.full_name,
        'image': user.image,
        'designation': user.designation,
        'phone': user.phone,
        'manager_name': user.parent.full_name if user.parent else None,
        'manager_id': user.parent.id if user.parent else None,
        'manager_image': user.parent.image if user.parent else None,
        'manager_designation': user.parent.designation if user.parent else None,
        'role': user.role,
    }


def get_resource_details(agent):
    last_location = agent.userstate.last_location
    agent_details = {
        'id': agent.id,
        'full_name': agent.full_name,
        'image': agent.image,
        'designation': agent.designation,
        'phone': agent.phone,
        'manager_name': agent.parent.full_name if agent.parent else None,
        'manager_id': agent.parent.id if agent.parent else None,
        'manager_image': agent.parent.image if agent.parent else None,
        'manager_designation': agent.parent.designation if agent.parent else None,
        'role': agent.role,
        'is_unreachable': agent.is_awol,
        'is_free': not agent.is_working,
        'presence': agent.is_present,
        'point': last_location.point if last_location else None,
        'address': last_location.address if last_location else '',
        'timestamp': last_location.timestamp if last_location else None,
    }
    return agent_details


def get_resource_list(agents):
    agent_list = []
    for agent in agents:
        active_task = agent.userstate.active_task
        last_location = agent.userstate.last_location
        agent_list.append({
            'id': agent.id,
            'full_name': agent.full_name,
            'image': agent.image,
            'is_unreachable': agent.is_awol,
            'is_free': not agent.is_working,
            'is_active': agent.is_active,
            'presence': agent.is_present,
            'point': last_location.point if last_location else None,
            'task_id': active_task.id if active_task else None,
            'task_title': active_task.title if active_task else None,
            'event': last_location.event if last_location else None,
            'address': last_location.address if last_location else '',
            'timestamp': last_location.timestamp if last_location else None,
        })
    return agent_list


def get_profile_details(user):
    package = user.org.subscription.current_usage.package if user.org else None
    renew_needed = user.org.subscription.renew_needed if user.org else False
    if user.role == ROLE_DICT['Employee']:
        app_info = AppInfo.objects.filter(app_name='agent')
    else:
        app_info = AppInfo.objects.filter(app_name='manager')
    if len(app_info) > 0:
        current_version = app_info[0].current_version
    else:
        current_version = -1
    user_details = {
        'id': user.id,
        'username': get_username(user),
        'full_name': user.full_name,
        'phone': user.phone,
        'image': user.image,
        'email': user.email,
        'domain_choices': DOMAIN_CONF,
        'domain': user.domain,
        'location_interval': user.org.location_interval,
        'presence': user.is_present,

        'org_id': user.org.id if user.org else None,
        'oid': user.org.oid if user.org else None,
        'org_name': user.org.org_name if user.org else None,
        'day_start': str(user.org.day_start) if user.org else None,
        'day_end': str(user.org.day_end) if user.org else None,
        'org_set': user.org.org_set,
        'org_logo': user.org.logo,

        'task_templates': TASK_TYPE[user.domain],
        'other_templates': get_other_templates(user),

        'manager_id': user.parent.id if user.parent else None,
        'manager_name': user.parent.full_name if user.parent else None,
        'manager_image': user.parent.image if user.parent else None,

        'role': user.role,
        'packages': PACKAGE_INFO,
        'package_info': PACKAGE_INFO[package] if (package and package in [1, 2, 3, 4]) else None,
        'renew_needed': renew_needed,
        'has_password': user.has_usable_password(),
        'tracking_enabled': user.org.tracking_enabled,
        'current_version': current_version
    }
    return user_details
