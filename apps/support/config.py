from apps.common.config import get_choices

SUPPORT_STATUS_DICT = {
    'Pending': 0,
    'In progress': 1,
    'Resolved': 2,
}


SUPPORT_STATUS_CHOICES = get_choices(SUPPORT_STATUS_DICT)
