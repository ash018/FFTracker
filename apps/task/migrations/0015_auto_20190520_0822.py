# Generated by Django 2.2 on 2019-05-20 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0014_auto_20190516_0613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(5, 'Postponed'), (0, 'Unassigned'), (4, 'Cancelled'), (3, 'Complete'), (2, 'In progress'), (1, 'Remaining')], default=0),
        ),
    ]
