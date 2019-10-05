# Generated by Django 2.2 on 2019-05-22 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0016_auto_20190522_0449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(5, 'New Task'), (7, 'Alert'), (0, 'Deadline crossed'), (2, 'Task cancelled'), (11, 'Assignment Modified'), (6, 'SOS'), (3, 'Task postponed'), (10, 'Assignment Created'), (8, 'Task started'), (1, 'Unreachable'), (4, 'Near Deadline'), (12, 'New Comment'), (9, 'Task finished'), (13, 'Force Offline')], default=7),
        ),
    ]
