# Generated by Django 2.2 on 2019-05-25 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0018_auto_20190525_0739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Unreachable'), (10, 'Assignment Created'), (4, 'Near Deadline'), (11, 'Assignment Modified'), (0, 'Deadline crossed'), (6, 'SOS'), (12, 'New Comment'), (8, 'Task started'), (13, 'Force Offline'), (9, 'Task finished'), (5, 'New Task'), (3, 'Task postponed'), (2, 'Task cancelled'), (7, 'Alert')], default=7),
        ),
    ]
