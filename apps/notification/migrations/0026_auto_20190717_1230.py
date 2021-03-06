# Generated by Django 2.2 on 2019-07-17 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0025_auto_20190704_0508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(21, 'Ping Device'), (5, 'New Task'), (12, 'New Comment'), (3, 'Task postponed'), (13, 'Force Offline'), (0, 'Deadline crossed'), (11, 'Assignment Modified'), (1, 'Unreachable'), (9, 'Task finished'), (6, 'SOS'), (2, 'Task cancelled'), (4, 'Near Deadline'), (10, 'Assignment Created'), (8, 'Task started'), (7, 'Alert')], default=7),
        ),
    ]
