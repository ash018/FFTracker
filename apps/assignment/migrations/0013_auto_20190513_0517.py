# Generated by Django 2.2 on 2019-05-13 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0012_auto_20190505_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(3, 'Complete'), (1, 'Remaining'), (4, 'Cancelled'), (2, 'In progress')], default=1),
        ),
    ]
