from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import logging

from apps.state.models import UserState
from apps.user.models import User

task_logger = logging.getLogger('task_logger')


def create_userstate_bg(caller):
    users = User.objects.filter()
    task_logger.info('Starting users loop......')
    for user in users:
        try:
            state = user.userstate
        except:
            userstate = UserState.objects.create(
                user=user
            )


class Command(BaseCommand):
    help = 'Create userstate'

    def handle(self, *args, **options):
        create_userstate_bg(self)
        msg = 'Successfully Finished creating userstates....'
        task_logger.info(msg)
        self.stdout.write(self.style.SUCCESS(msg))

