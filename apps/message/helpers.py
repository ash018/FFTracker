import random
import string
from django.db.models import Q


def get_group_members(message, user):
    members = []
    members_qs = message.group.members.filter(
        ~Q(id=user.id)
    )
    for mem in members_qs:
        members.append(mem.id)
    return members


def get_message_content(message):
    details = {
        'text': message.text,
        'attachments': message.attachments,
        'sender_id': message.sender_id,
        'sender_name': message.sender.full_name,
        'sender_image': message.sender.image,
        'timestamp': str(message.timestamp),
        'thread_id': message.group_id,
        'seen': False
    }
    return details


def get_message_list(message_objs):
    message_list = []
    for msg in message_objs:
        message_list.append(get_message_content(msg))
    return message_list


def get_thread_content(message, user):
    details = {
        'text': message.text,
        'attachments': message.attachments,
        'type': message.type,
        'timestamp': str(message.timestamp),
        'thread_id': message.group_id,
        'seen': False,
    }
    if message.type == 0:
        partner = message.group.members.filter(~Q(id=user.id)).first()
        details.update({
            'partner_name': partner.full_name,
            'partner_image': partner.image,
            'partner_status': partner.is_present,
            'partner_id': partner.id,
        })
    else:
        details.update({
            'group_name': message.group.name,
            'members': get_group_members(message, user)
            # 'group_admin': message.group.admin.full_name,
        })
    return details


def get_rand_str(str_len):
    return ''.join(
        random.sample(
            string.ascii_uppercase + string.digits,
            k=str_len
        )
    )
