# Generated by Django 2.2 on 2019-05-16 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0013_auto_20190513_0517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(2, 'In progress'), (0, 'Unassigned'), (5, 'Postponed'), (1, 'Remaining'), (4, 'Cancelled'), (3, 'Complete')], default=0),
        ),
    ]
