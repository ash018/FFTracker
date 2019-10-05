import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.models import Q

from apps.task.models import Task
from apps.notification.transmitters import task_delayed_notification
from apps.task.config import TASK_STATUS_DICT as TSD

task_logger = logging.getLogger('task_logger')


def check_delayed_tasks_bg(caller):
    valid_list = [TSD['Unassigned'], TSD['In progress'], TSD['Remaining']]
    tasks = Task.objects.select_related(
        'manager'
    ).prefetch_related(
        'agent_list'
    ).filter(
        Q(status__in=valid_list) &
        Q(delayed=False)
    )
    task_logger.info('Starting delayed task iteration.....')
    this_time = timezone.datetime.now()
    task_logger.info('Delayed task timestamp: ' + str(this_time))
    task_count = 0
    for task in tasks:
        if task.deadline < timezone.now():
            task.delayed = True
            task.save()
            task_delayed_notification(task)
            task_count += 1
    task_logger.info('Total delayed tasks: ' + str(task_count))


class Command(BaseCommand):
    help = 'Get delayed tasks'

    def handle(self, *args, **options):
        check_delayed_tasks_bg(self)

        msg = 'Successfully Finished get delayed tasks....'
        task_logger.info(msg)
        self.stdout.write(self.style.SUCCESS(msg))
