from firebase_admin import messaging


NOTIFICATION_DICT = {
    'Deadline crossed': 0,
    'Unreachable': 1,
    'Task cancelled': 2,
    'Task postponed': 3,
    'Near Deadline': 4,
    'New Task': 5,
    'SOS': 6,
    'Alert': 7,
    'Task started': 8,
    'Task finished': 9,
    'Assignment Created': 10,
    'Assignment Modified': 11,
    'New Comment': 12,
    'Force Offline': 13,
    'Ping Device': 21,
}
NOTIFICATION_CHOICES = tuple((value, key) for key, value in NOTIFICATION_DICT.items())


def get_ntf_title(type_int):
    for k, v in NOTIFICATION_DICT.items():
        if v == type_int:
            return k
    else:
        return None


def send_notification(notification):
    try:
        message = messaging.Message(
            data={
                'type': 'notification',
                'notification_type': str(notification.type),
                'title': str(NOTIFICATION_CHOICES[notification.type][1]),
                'body': str(notification.text)
            },
            token=notification.recipient.fb_token,
        )
        resp = messaging.send(message)
    except Exception as e:
        resp = str(e)
    return resp

