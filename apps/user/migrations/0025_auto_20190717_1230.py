# Generated by Django 2.2 on 2019-07-17 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0024_auto_20190704_0508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='domain',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Sales'), (3, 'Rent-a-car/Ride sharing'), (2, 'Installation/Maintenance/Repair'), (4, 'Insurance'), (1, 'Delivery Service'), (5, 'Others'), (6, 'Sales(Pharma)')], default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(2, 'Employee'), (3, 'Leader'), (1, 'Manager'), (0, 'Organizer')], default=2),
        ),
    ]
