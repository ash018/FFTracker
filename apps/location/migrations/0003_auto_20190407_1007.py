# Generated by Django 2.2 on 2019-04-07 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0002_auto_20190407_0310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='event',
            field=models.PositiveSmallIntegerField(choices=[(5, 'Start task'), (7, 'Off OOC'), (8, 'In OOC'), (3, 'To Offline'), (4, 'To OOC'), (2, 'No Task'), (0, 'To Online'), (1, 'On Task'), (6, 'Finish task')], default=2),
        ),
    ]
