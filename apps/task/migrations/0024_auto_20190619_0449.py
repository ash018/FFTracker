# Generated by Django 2.2 on 2019-06-19 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0023_auto_20190609_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(2, 'In progress'), (4, 'Cancelled'), (5, 'Postponed'), (3, 'Complete'), (1, 'Remaining'), (0, 'Unassigned')], default=0),
        ),
    ]
