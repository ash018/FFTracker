from django.db.models import Q
from apps.user.models import User
from apps.user.config import ROLE_DICT
from apps.task.config import TASK_STATUS_DICT as TSD


def get_task_qf(user):
    if user.role == ROLE_DICT['Organizer']:
        task_qf = Q(org=user.org)
    else:
        task_qf = Q(
            agent_list=user
        ) | (
            Q(manager=user.parent) &
            ~Q(manager=None) &
            Q(status=TSD['Unassigned'])
        )

        if user.role == ROLE_DICT['Manager']:
            task_qf |= Q(manager=user)
    return task_qf


def task_filter(request):
    task_qf = get_task_qf(request.user)
    if request.query_params.get('delayed'):
        delayed_list = [TSD['Cancelled'], TSD['Postponed'], TSD['Complete']]
        task_qf &= (
            Q(delayed=True) & ~Q(status__in=delayed_list)
        )
    if request.query_params.get('status'):
        status = request.query_params.get('status')
        task_qf &= (Q(status=status))

    if request.query_params.get('token'):
        token = request.query_params.get('token')
        task_qf &= (
            Q(title__icontains=token) |
            Q(address__icontains=token)
        )

    # if request.query_params.get('deadline'):
    #     deadline = request.query_params.get('deadline')
    #     task_qf &= (Q(deadline__day=deadline))

    if request.query_params.get('agent_id'):
        agent_id = request.query_params.get('agent_id')
        agent = User.objects.get(id=agent_id)
        task_qf &= Q(agent_list=agent)

    if request.query_params.get('manager_id'):
        manager_id = request.query_params.get('manager_id')
        task_qf &= Q(manager_id=manager_id)

    return task_qf