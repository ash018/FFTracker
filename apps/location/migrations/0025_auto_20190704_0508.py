# Generated by Django 2.2 on 2019-07-04 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0024_auto_20190619_0449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='event',
            field=models.PositiveSmallIntegerField(choices=[(6, 'Finish task'), (21, 'Ping Server'), (1, 'On Task'), (2, 'No Task'), (3, 'To Offline'), (7, 'Off OOC'), (4, 'To OOC'), (5, 'Start task'), (8, 'In OOC'), (0, 'To Online')], default=2),
        ),
    ]
