# Generated by Django 2.2 on 2019-05-22 09:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0015_auto_20190522_0449'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datausage',
            old_name='megabytes',
            new_name='device_megabytes',
        ),
        migrations.AddField(
            model_name='datausage',
            name='date',
            field=models.DateField(db_index=True, default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='datausage',
            name='instant_megabytes',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='datausage',
            name='total_megabytes',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='user',
            name='domain',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Sales'), (4, 'Insurance'), (6, 'Sales(Pharma)'), (5, 'Others'), (1, 'Delivery Service'), (2, 'Installation/Maintenance/Repair'), (3, 'Rent-a-car/Ride sharing')], default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(2, 'Employee'), (1, 'Manager'), (0, 'Organizer'), (3, 'Leader')], default=2),
        ),
    ]
