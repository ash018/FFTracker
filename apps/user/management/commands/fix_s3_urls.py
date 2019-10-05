from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import logging

from apps.state.models import UserState
from apps.user.models import User
from apps.task.models import Task
from apps.org.models import Organization

task_logger = logging.getLogger('task_logger')


def change_url(s3_file):
    return s3_file.replace('/teamworkfiles/', '/teamworkfiles-new/')


def fix_s3_urls_user_image_bg(caller):
    users = User.objects.filter()
    task_logger.info('Starting users loop......')
    for user in users:
        try:
            if user.image:
                user.image = change_url(user.image)
                user.save()
        except Exception as e:
            error = 'ERROR for user: ' + user.username + ', ' + str(e)
            caller.stdout.write(error)


def fix_s3_urls_user_org_logo(caller):
    orgs = Organization.objects.all()
    task_logger.info('Starting org loop......')
    for org in orgs:
        try:
            if org.logo:
                org.logo = change_url(org.logo)
                org.save()
        except Exception as e:
            error = 'ERROR for org: ' + org.oid + ', ' + str(e)
            caller.stdout.write(error)


def fix_s3_urls_task_files_bg(caller):
    tasks = Task.objects.filter()
    task_logger.info('Starting tasks loop......')
    for task in tasks:
        mgr_images = task.images
        if mgr_images:
            mgr_images_new = []
            for mgr_img in mgr_images:
                mgr_images_new.append(change_url(mgr_img))
            task.images = mgr_images_new

        custom_fields = task.custom_fields
        if 'image_urls' in custom_fields.keys() and custom_fields['image_urls']:
            agt_images_new = []
            for agt_img in custom_fields['image_urls']:
                try:
                    agt_img['url'] = change_url(agt_img['url'])
                    agt_images_new.append(agt_img)
                except Exception as e:
                    error = 'ERROR for task image: ' + task.title + ', ' + str(e)
                    caller.stdout.write(str(error))

            custom_fields['image_urls'] = agt_images_new

        if 'attachment_urls' in custom_fields.keys() and custom_fields['attachment_urls']:
            custom_fields['attachment_urls'] = change_url(custom_fields['attachment_urls'])

        task.custom_fields = custom_fields
        task.save()


class Command(BaseCommand):
    help = 'Fix S3 URLs'

    def handle(self, *args, **options):
        # fix_s3_urls_user_image_bg(self)
        # msg = 'Successfully Finished fixing S3 profile URLs....'
        # task_logger.info(msg)
        # self.stdout.write(self.style.SUCCESS(msg))
        #
        # fix_s3_urls_task_files_bg(self)
        # msg = 'Successfully Finished fixing S3 task file URLs....'
        # task_logger.info(msg)
        # self.stdout.write(self.style.SUCCESS(msg))

        fix_s3_urls_user_org_logo(self)
        msg = 'Successfully Finished fixing S3 org logo URLs....'
        task_logger.info(msg)

        self.stdout.write(self.style.SUCCESS(msg))
