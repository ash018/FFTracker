# Generated by Django 2.2 on 2019-04-11 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0006_auto_20190408_0925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Remaining'), (2, 'In progress'), (4, 'Cancelled'), (0, 'Unassigned'), (3, 'Complete'), (5, 'Postponed')], default=0),
        ),
    ]
