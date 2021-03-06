# Generated by Django 2.2 on 2019-07-24 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0026_auto_20190717_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(4, 'Near Deadline'), (6, 'SOS'), (3, 'Task postponed'), (7, 'Alert'), (11, 'Assignment Modified'), (10, 'Assignment Created'), (2, 'Task cancelled'), (8, 'Task started'), (1, 'Unreachable'), (12, 'New Comment'), (5, 'New Task'), (0, 'Deadline crossed'), (21, 'Ping Device'), (13, 'Force Offline'), (9, 'Task finished')], default=7),
        ),
    ]
