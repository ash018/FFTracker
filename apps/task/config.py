from django.utils import timezone
from apps.common.config import get_choices


TASK_STATUS_DICT = {
    'Unassigned': 0,
    'Remaining': 1,
    'In progress': 2,
    'Complete': 3,
    'Cancelled': 4,
    'Postponed': 5
}


def get_task_status(status):
    for k, v in TASK_STATUS_DICT.items():
        if v == status:
            return k
    else:
        return None


TASK_STATUS_CHOICES = get_choices(TASK_STATUS_DICT)


def default_duration():
    return timezone.now() + timezone.timedelta(hours=2)