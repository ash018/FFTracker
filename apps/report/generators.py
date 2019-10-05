from apps.report.helpers import *
from .config import get_attendance_status
from apps.task.config import get_task_status


def attendance_report_full(request):
    ati_qs = get_ati_qs(request).order_by('date')
    attendance_data = []
    for ati in ati_qs:
        cur_ati = {
            'date': ati.date,
            'agent': ati.user.full_name,
            'manager': ati.user.parent.full_name if ati.user.parent else 'None',
            'status': get_attendance_status(ati.status),
            'entry_time': str(ati.init_entry_time),
            'exit_time': str(ati.exit_time) if ati.exit_time else 'None',
            'work_hour': str(ati.work_hour).split('.')[0] if ati.work_hour else 'None',
        }
        attendance_data.append(cur_ati)

    return attendance_data


def task_report_full(request):
    task_qs = get_task_qs(request).order_by('date')
    full_task_report = []
    for task in task_qs:
        for agent in task.agent_list.all():
            current_task = {
                'date': str(task.date),
                'title': task.title,
                'agent': agent.full_name,
                'expected_duration': str(task.deadline - task.start).split('.')[0],
                'address': task.address if task.address else 'None',
                'status': get_task_status(task.status),
                'delayed': 'Yes' if task.delayed else 'No'
            }
            try:
                current_task.update({
                    'actual_duration': str(task.ts_finish - task.ts_start).split('.')[0],
                })
            except Exception as e:
                current_task.update({
                    'actual_duration': 'None',
                })
            full_task_report.append(current_task)
    return full_task_report

