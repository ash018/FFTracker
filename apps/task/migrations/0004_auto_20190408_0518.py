# Generated by Django 2.2 on 2019-04-08 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0003_auto_20190407_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(5, 'Postponed'), (3, 'Complete'), (0, 'Unassigned'), (1, 'Remaining'), (2, 'In progress'), (4, 'Cancelled')], default=0),
        ),
    ]
