# Generated by Django 2.2 on 2019-06-19 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0022_auto_20190609_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='domain',
            field=models.PositiveSmallIntegerField(choices=[(2, 'Installation/Maintenance/Repair'), (6, 'Sales(Pharma)'), (1, 'Delivery Service'), (4, 'Insurance'), (0, 'Sales'), (3, 'Rent-a-car/Ride sharing'), (5, 'Others')], default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Organizer'), (3, 'Leader'), (1, 'Manager'), (2, 'Employee')], default=2),
        ),
    ]
