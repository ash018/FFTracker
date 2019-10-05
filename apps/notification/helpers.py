from django.db.models import Q
from .models import Notification
from .config import NOTIFICATION_DICT as NTD, NOTIFICATION_CHOICES as NTC
from apps.location.config import get_address


def get_notification_content(ntf):

    ntf_content = {
        'ntf_id': ntf.id,
        'type': ntf.type,
        'point': ntf.point,
        'address': ntf.address,

        'task_id': ntf.task_id if ntf.task else None,
        'task_title': ntf.task.title if ntf.task else '',

        'agent_id': ntf.agent_id if ntf.agent else None,
        'agent_name': ntf.agent.full_name if ntf.agent else '',
        'agent_phone': ntf.agent.phone if ntf.agent else None,

        'assignment_id': ntf.assignment_id if ntf.assignment else None,
        'assignment_title': ntf.assignment.title if ntf.assignment else '',

        'timestamp': str(ntf.timestamp),
        'text': ntf.text,
        'images': ntf.images,
        'checked': ntf.checked,
    }

    return ntf_content


def get_ntf_list(ntf_qs):
    ntf_list = []
    for ntf in ntf_qs:
        ntf_list.append(get_notification_content(ntf))
    return ntf_list


def create_notification(agent, ntf_type, recipients):
    text = 'Agent just became unreachable!'
    for rcpt in recipients:
        ntf = Notification.objects.create(
            type=ntf_type,
            title=NTC[ntf_type][1],
            agent=agent,
            recipient=rcpt,
            text=text
        )
    return ntf


def get_unchecked_count(request):
    ntf_qs = Notification.objects.filter(Q(recipient=request.user))
    unchecked = ntf_qs.filter(Q(checked=False)).count()
    return unchecked
