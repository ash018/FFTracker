from django.db.models import Q
from apps.user.models import User
from apps.state.models import UserState
from apps.task.models import Task
from apps.task.config import TASK_STATUS_DICT as TSD


DEF_LIMIT = 50


# Task Assignment Helpers
def set_agent_list_in_task(agent_list, task):
    # print(agent_list)
    task.save()
    task.agent_list.clear()
    if len(agent_list) > 0:
        task.status = TSD['Remaining']
    else:
        task.status = TSD['Unassigned']
    for agent in agent_list:
        if agent not in task.agent_list.all():
            task.agent_list.add(agent)
    task.save()


def unset_active_task(task):
    for agent in task.agent_list.all():
        User.objects.filter(
            id=agent.id
        ).update(is_working=False)
        UserState.objects.filter(
            user=agent
        ).update(active_task=None)


def set_active_task(task):
    for agent in task.agent_list.all():
        User.objects.filter(
            id=agent.id
        ).update(is_working=True)
        UserState.objects.filter(
            user=agent
        ).update(active_task=task)


def check_active_task(task):
    for agent in task.agent_list.all():
        task_qs = Task.objects.filter(
            Q(agent_list=agent) &
            Q(status=TSD['In progress'])
        )
        if task_qs.exists():
            return False
    return True


def task_list_qs(task_qf):
    task_qs = Task.objects.defer(
        'creator', 'ts_start', 'ts_finish', 'custom_fields',
        'images', 'point_finish', 'point_start',
    ).select_related(
        'manager'
    ).prefetch_related(
        'agent_list'
    ).filter(
        task_qf
    ).order_by('-deadline').distinct()

    return task_qs


def get_task_details(task):
    manager = task.manager
    agent_list = []
    for agent in task.agent_list.all():
        agent_list.append({
            'id': agent.id,
            'image': agent.image,
            'name': agent.full_name,
        })
    task_details = {
        'id': task.id,
        'title': task.title,
        'point': task.point,
        'status': task.status,
        'start': str(task.start),
        'deadline': str(task.deadline),
        'started': str(task.ts_start) if task.ts_start else None,
        'finished': str(task.ts_finish) if task.ts_finish else None,
        'images': task.images,
        'task_type': task.task_type,
        'agent_list': agent_list,
        'manager': manager.full_name if manager else 'None',
        'manager_id': manager.id if manager else None,
        'image_required': task.image_required,
        'attachment_required': task.attachment_required,
        'custom_fields': task.custom_fields,
        'delayed': task.delayed,
        'address': task.address
    }
    return task_details


def get_task_list(tasks):
    task_list = []
    for task in tasks:
        manager = task.manager
        agent_list = []
        for agent in task.agent_list.all():
            agent_list.append({
                'id': agent.id,
                'image': agent.image,
                'name': agent.full_name,
            })
        task_data = {
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'deadline': str(task.deadline),
            'started': str(task.ts_start) if task.ts_start else None,
            'finished': str(task.ts_finish) if task.ts_finish else None,
            'task_type': task.task_type,
            'agent_list': agent_list,
            'manager': manager.full_name if manager else 'None',
            'manager_id': manager.id if manager else None,
            'delayed': task.delayed,
            'address': task.address,
            'point': task.point,
        }
        task_list.append(task_data)
    return task_list


def get_template_data(template):
    template_data = {
        'id': template.id,
        'task_type': template.task_type,
        'task_fields': template.task_fields,
    }
    return template_data


def create_task(title, manager,  agent_list=[], status=TSD['Unassigned'], task_type='Visit'):
    task = Task(
        title=title,
        task_type=task_type,
        manager=manager,
        status=status,
        org=manager.org,
    )
    task.save()
    if len(agent_list) > 0 and status == TSD['Unassigned']:
        task.status = TSD['Remaining']
    for agent in agent_list:
        agent.is_present = True
        if status == TSD['In progress']:
            agent.userstate.active_task = task
            agent.is_working = True
            agent.save()
            agent.userstate.save()
        task.agent_list.add(agent)
    task.save()
    return task
