from django.db.models import Q
from apps.user.models import User
from apps.user.config import ROLE_DICT


def get_assignment_qf(user):
    if user.role == ROLE_DICT['Organizer']:
        qf_assignment = Q(
            org=user.org
        )
    else:
        qf_assignment = Q(
            manager=user
        ) | Q(
            assignee_list=user
        ) | Q(
            assignee=user
        ) | Q(
            creator=user
        )
    return qf_assignment


def assignment_filter(request):
    assignment_qf = get_assignment_qf(request.user)

    if request.query_params.get('status'):
        status = request.query_params.get('status')
        assignment_qf &= (Q(status=status))

    if request.query_params.get('token'):
        token = request.query_params.get('token')
        assignment_qf &= (
            Q(title__icontains=token)
            # Q(address__icontains=token)
        )

    if request.query_params.get('assignee_id'):
        assignee_id = request.query_params.get('assignee_id')
        assignee = User.objects.get(id=assignee_id)
        assignment_qf &= (Q(assignee_list=assignee) | Q(assignee=assignee))

    if request.query_params.get('manager_id'):
        manager_id = request.query_params.get('manager_id')
        assignment_qf &= Q(manager_id=manager_id)

    return assignment_qf
