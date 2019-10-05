from django.utils import timezone
from apps.common.config import get_choices


ASSIGNMENT_STATUS_DICT = {
    'Remaining': 1,
    'In progress': 2,
    'Complete': 3,
    'Cancelled': 4,
}

ASSIGNMENT_STATUS_CHOICES = get_choices(ASSIGNMENT_STATUS_DICT)


def default_deadline():
    return timezone.now() + timezone.timedelta(days=1)


def empty_list():
    return []

