import pytz
from rest_framework.exceptions import NotAcceptable, ValidationError
from django.db.models import Q
from django.utils import timezone
from .models import AttendanceCombined as ATC, \
    AttendanceIndividual as ATI, Ranking
from .config import ATTENDANCE_STATUS_DICT as ASD, RANGE_DICT
from apps.task.models import Task
from apps.user.auth_helpers import get_username

utc = pytz.UTC


def get_ranking_details(top_five, topic):
    user_list = []
    for obj in top_five:
        data = {
            'topic': topic,
            'id': obj.user_id,
            'username': get_username(obj.user),
            'agent_name': obj.user.full_name,
            'image': obj.user.image,
            topic: getattr(obj, topic, None),
        }
        user_list.append(data)
    return user_list


def get_work_hours(org):
    start_time = org.day_start
    end_time = org.day_end
    today = timezone.datetime.now().date()
    work_hours = timezone.datetime.combine(today, end_time) - \
                 timezone.datetime.combine(today, start_time)
    return work_hours


def set_start_end(start, weekend):
    while not (start.weekday() in weekend):
        # print('Cur start: ', start.weekday())
        start -= timezone.timedelta(days=1)
    end = start + timezone.timedelta(days=7)
    return start, end


def last_day_of_month(date):
    if date.month in [4, 6, 9, 11]:
        return 30
    if date.month == 2:
        if date.year % 4 == 0:
            return 29
        else:
            return 28
    return 31


def start_end(q_date, weekend, range_int):
    start, end = q_date, q_date
    if range_int == RANGE_DICT['last_day']:
        start = q_date
        end = q_date

    elif range_int == RANGE_DICT['this_week']:
        start, end = set_start_end(q_date, weekend)

    elif range_int == RANGE_DICT['last_week']:
        q_date = q_date - timezone.timedelta(days=7)
        start, end = set_start_end(q_date, weekend)

    elif range_int == RANGE_DICT['this_month']:
        start = timezone.datetime(q_date.year, q_date.month, 1)
        start = utc.localize(start)
        end = q_date

    elif range_int == RANGE_DICT['last_month']:
        if q_date.month > 1:
            last_month = q_date.month - 1
            year = q_date.year
        else:
            last_month = 12
            year = q_date.year - 1
        start = timezone.datetime(year, last_month, 1)
        start = utc.localize(start)
        end = timezone.datetime(year, last_month, last_day_of_month(start))
        end = utc.localize(end)

    end += timezone.timedelta(hours=23)
    return start, end


def get_attendance_list(user_objs, date):
    attendance_list = []
    for user in user_objs:
        attendance_details = {
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
            'date': str(date),
        }
        attendance_list.append(attendance_details)
    return attendance_list


def get_atc_qs(request):
    manager = request.query_params.get('manager', False)
    date = request.query_params.get('date', False)
    field = request.query_params.get('field', False)
    date_range = request.query_params.get('date_range', 1)

    if (not manager) or (not date):
        msg = 'Provide the query parameters!'
        raise ValidationError(detail=msg)

    if not date:
        date = timezone.now() - timezone.timedelta(days=1)
    else:
        date = timezone.datetime.strptime(date, '%Y-%m-%d')
        date = utc.localize(date)

    # print(date)
    weekend = request.user.org.weekend
    start, end = start_end(date, weekend, int(date_range))
    date_list = []
    cur_date = start
    while cur_date <= end:
        date_list.append(cur_date.date())
        cur_date = cur_date + timezone.timedelta(days=1)
    # print(date_list)

    atc_filter = Q(
        date__in=date_list
    ) & Q(
        org_id=request.user.org_id
    )

    atc_qs = ATC.objects.filter(atc_filter)
    if not atc_qs.exists():
        msg = 'Report not found!'
        raise ValidationError(detail=msg)
    # atc_obj = atc_qs[0]
    manager_qf = Q(parent_id=manager)
    return atc_qs, manager_qf, field


def get_ati_qs(request):
    agent = request.query_params.get('agent', False)
    manager = request.query_params.get('manager', False)
    date = request.query_params.get('date', False)
    date_range = request.query_params.get('date_range', 1)

    if (not manager) and (not agent):
        raise ValidationError(detail='Provide manager or agent id!')

    ati_qf = Q()
    if manager:
        ati_qf &= Q(user__parent_id=manager)

    if agent:
        ati_qf &= Q(user_id=agent)

    if not date:
        date = timezone.now() - timezone.timedelta(days=1)
    else:
        date = timezone.datetime.strptime(date, '%Y-%m-%d')
        date = utc.localize(date)

    # print(date)

    weekend = request.user.org.weekend
    start, end = start_end(date, weekend, int(date_range))
    date_list = []
    cur_date = start
    while cur_date <= end:
        date_list.append(cur_date.date())
        cur_date = cur_date + timezone.timedelta(days=1)

    ati_qs = ATI.objects.filter(
        Q(date__in=date_list) &
        ati_qf
    )

    return ati_qs


def get_ranking_qs(request):
    manager = request.query_params.get('manager', False)
    date = request.query_params.get('date', False)
    topic = request.query_params.get('topic', False)
    date_range = request.query_params.get('date_range', 2)

    if (not manager) or (not topic):
        msg = 'Provide the query parameters!'
        raise ValidationError(detail=msg)
    valid_topics = [
        'absence',
        'low_task_hour',
        'low_work_hour',
        'overtime',
        'late_arrival',
        'delayed_task',
        'travel_distance'
    ]
    if topic not in valid_topics:
        msg = 'Invalid topic!'
        raise ValidationError(detail=msg)

    if not date:
        date = timezone.now() - timezone.timedelta(days=1)
    else:
        date = timezone.datetime.strptime(date, '%Y-%m-%d')
        date = utc.localize(date)

    rnk_filter = Q(
        user__parent_id=manager
    ) & Q(
        date_range=date_range
    ) & Q(
        date=date
    )

    ranking_qs = Ranking.objects.filter(rnk_filter).order_by('-' + topic)[0:5]
    return ranking_qs, topic


def get_task_qs(request):
    manager = request.query_params.get('manager', False)
    date = request.query_params.get('date', False)
    date_range = request.query_params.get('date_range', 2)
    agent = request.query_params.get('agent', False)
    status = request.query_params.get('status', False)
    delayed = request.query_params.get('delayed', False)

    if (not manager) and (not agent):
        raise ValidationError(detail='Provide manager or agent id!')

    task_qf = Q()
    if manager:
        task_qf &= Q(manager_id=manager)

    if agent:
        # agent = User.objects.get(id=agent)
        task_qf &= Q(agent_list=agent)

    if status:
        task_qf &= Q(status=status)

    if delayed:
        task_qf &= Q(delayed=True)

    if not date:
        date = timezone.now() - timezone.timedelta(days=1)
    else:
        date = timezone.datetime.strptime(date, '%Y-%m-%d')
        date = utc.localize(date)

    weekend = request.user.org.weekend
    # if int(date_range) != RANGE_DICT['last_day']:
    #     date = timezone.now() - timezone.timedelta(days=1)

    start, end = start_end(date, weekend, int(date_range))

    task_qf &= Q(deadline__gte=start) & Q(deadline__lte=end)

    task_qs = Task.objects.filter(task_qf)
    return task_qs


def create_attendance(
        agent,
        status=ASD['Present'],
        work_hour=timezone.timedelta(hours=9),
        task_hour_p=70.0,
        late_arrival=False,
        date=timezone.now()):

    ati = ATI.objects.create(
        date=date.date(),
        init_entry_time=date,
        last_entry_time=date,
        user=agent, org=agent.org,
        late_arrival=late_arrival,
        status=status,
        task_hour_p=task_hour_p,
        work_hour=work_hour,
        exit_time=date + work_hour
    )
