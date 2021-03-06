# Generated by Django 2.2 on 2019-05-05 11:54

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0010_auto_20190502_0455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='date',
            field=models.DateField(db_index=True, default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='location',
            name='event',
            field=models.PositiveSmallIntegerField(choices=[(1, 'On Task'), (3, 'To Offline'), (5, 'Start task'), (6, 'Finish task'), (4, 'To OOC'), (0, 'To Online'), (7, 'Off OOC'), (2, 'No Task'), (8, 'In OOC')], default=2),
        ),
        migrations.AlterField(
            model_name='location',
            name='timestamp',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
    ]
