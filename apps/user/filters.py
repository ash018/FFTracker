from django.db.models import Q
from django.utils import timezone

from apps.user.models import User
from apps.user.config import ROLE_DICT


def get_users_qf(organizer):
    users_qf = Q(org=organizer.org)
    users_qf &= Q(role__in=[ROLE_DICT['Manager'], ROLE_DICT['Employee']])
    return users_qf


def resource_filter(request):
    user = request.user
    qf_resource = Q(parent=user) & Q(is_active=True)
    query_status = request.query_params.get('status')
    if query_status == 'online' or query_status == 'present':
        qf_resource &= Q(is_present=True)
    elif query_status == 'offline' or query_status == 'absent':
        qf_resource &= Q(is_present=False)
    elif query_status == 'working':
        qf_resource &= (Q(is_present=True) & Q(is_working=True) & Q(is_awol=False))
    elif query_status == 'free':
        qf_resource &= (Q(is_present=True) & Q(is_working=False) & Q(is_awol=False))
    elif query_status == 'unreachable':
        qf_resource &= (Q(is_present=True) & Q(is_awol=True))
    else:
        pass
    return qf_resource


def account_filter(request):
    viewer = request.user
    role = request.query_params.get('role', None)
    manager_id = request.query_params.get('manager_id', None)
    token = request.query_params.get('token', None)

    if viewer.role == ROLE_DICT['Organizer']:
        users_qf = get_users_qf(viewer)
        users_qs = User.objects.select_related(
            'parent'
        ).filter(users_qf)
    else:
        users_qs = viewer.get_descendants(include_self=True)
        users_qs = users_qs.select_related(
            'parent'
        )
    if token:
        users_qs = users_qs.filter(
            Q(username__icontains=token) |
            Q(full_name__icontains=token)
        )

    if role:
        users_qs = users_qs.filter(Q(role=int(role)))

    if manager_id:
        if viewer.role == ROLE_DICT['Organizer'] and int(manager_id) == viewer.id:
            users_qs = users_qs.filter(Q(parent=None))
        else:
            users_qs = users_qs.filter(Q(parent_id=manager_id))

    return users_qs
