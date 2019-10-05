
from .models import Assignment
from .config import ASSIGNMENT_STATUS_DICT as ASD
# from rest_framework.exceptions import NotAcceptable, ValidationError


def get_comment_details(cmt):
    cmt_details = {
        'id': cmt.id,
        'timestamp': cmt.timestamp,
        'text': cmt.text,
        'attachments': cmt.attachments,
        'user': cmt.user.full_name,
        'image': cmt.user.image,
    }
    return cmt_details


def get_assignment_qs(assignment_qf):
    assignment_qs = Assignment.objects.defer(
        'description', 'creator', 'custom_fields'
    ).select_related(
        'manager', 'assignee'
    ).filter(
        assignment_qf
    ).order_by('-deadline')
    return assignment_qs


def get_assignee_list(assignment):
    assignee_list = []
    for assignee in assignment.assignee_list.all():
        assignee_list.append({
            'name': assignee.full_name,
            'id': assignee.id,
            'image': assignee.image,
        })
    return assignee_list


def get_assignment_data(assignment):
    manager = assignment.manager
    assignee = assignment.assignee

    # TODO: paginated comment list
    comment_list = []
    comment_objs = assignment.comment_set.all().order_by('timestamp')
    for cmt in comment_objs:
        comment_list.append(get_comment_details(cmt))
    assignment_data = {
        'id': assignment.id,
        'title': assignment.title,
        'description': assignment.description,
        'status': assignment.status,
        'created': str(assignment.created),
        'deadline': str(assignment.deadline),
        'custom_fields': assignment.custom_fields,
        'comment_list': comment_list,
        'progress': assignment.progress,

        'manager': manager.full_name if manager else 'None',
        'manager_id': manager.id if manager else None,
        'manager_image': manager.image if manager else None,

        'assignee': assignee.full_name if assignee else 'None',
        'assignee_id': assignee.id if assignee else None,
        'assignee_image': assignee.image if assignee else None,

        'assignee_list': get_assignee_list(assignment),
    }
    return assignment_data


def get_assignment_list(assignments):
    assignment_list = []
    for assignment in assignments:
        manager = assignment.manager
        assignee = assignment.assignee
        assignment_data = {
            'id': assignment.id,
            'title': assignment.title,
            'status': assignment.status,
            'deadline': str(assignment.deadline),
            'progress': assignment.progress,

            'manager': manager.full_name if manager else 'None',
            'manager_id': manager.id if manager else None,
            'manager_image': manager.image if manager else None,

            'assignee': assignment.assignee.full_name if assignee else 'None',
            'assignee_id': assignee.id if assignee else None,
            'assignee_image': assignee.image if assignee else None,

            'assignee_list': get_assignee_list(assignment)
        }
        assignment_list.append(assignment_data)
    return assignment_list


def create_assignment(manager, assignee_list, status=ASD['Remaining'], title='Assignment'):
    assignment = Assignment(
        title=title,
        manager=manager,
        status=status,
        org=manager.org,
        assignee=assignee_list[0],
    )
    assignment.save()
    assignment.assignee_list.add(*assignee_list)
    return assignment


