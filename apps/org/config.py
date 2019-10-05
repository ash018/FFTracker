from apps.common.config import get_choices

STATUS_CHOICES = (
    (1, 'Enabled'),
    (0, 'Disabled'),
    (2, 'Suspended')
)

WEEKDAY_DICT = {
    'Mon': 0,
    'Tue': 1,
    'wed': 2,
    'Thu': 3,
    'Fri': 4,
    'Sat': 5,
    'Sun': 6,
}

WEEKDAY_CHOICES = get_choices(WEEKDAY_DICT)


def default_weekend():
    return [WEEKDAY_DICT['Fri'], WEEKDAY_DICT['Sat']]
