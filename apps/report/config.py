from apps.common.config import get_choices

DATE_COEFF = 8
LOW_HOUR_COEFF = .95
OVERTIME_COEFF = 1.05

ATTENDANCE_STATUS_DICT = {
    'Absent': 0,
    'Present': 1,
    'Weekend': 2,
    'Holiday': 3,
    'On Leave': 4
}

ATTENDANCE_STATUS_CHOICES = get_choices(ATTENDANCE_STATUS_DICT)


def get_attendance_status(status):
    for k, v in ATTENDANCE_STATUS_DICT.items():
        if v == status:
            return k
    else:
        return None


RANKING_TOPIC_DICT = {
    'absence': 0,
    'late_arrival': 1,
    'low_work_hour': 2,
    'low_task_hour': 3,
    'delayed_task': 4,
    'overtime': 5,
    'travel_distance': 6
}


RANKING_TOPIC_CHOICES = get_choices(RANKING_TOPIC_DICT)

RANGE_DICT = {
    'last_day': 1,
    'this_week': 2,
    'last_week': 3,
    'this_month': 4,
    'last_month': 5
}

RANGE_CHOICES = get_choices(RANGE_DICT)
