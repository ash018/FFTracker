# Generated by Django 2.2 on 2019-05-13 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_auto_20190505_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='domain',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Delivery Service'), (3, 'Rent-a-car/Ride sharing'), (6, 'Sales(Pharma)'), (0, 'Sales'), (4, 'Insurance'), (5, 'Others'), (2, 'Installation/Maintenance/Repair')], default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(3, 'Leader'), (0, 'Organizer'), (1, 'Manager'), (2, 'Employee')], default=2),
        ),
    ]
