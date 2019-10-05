# Generated by Django 2.2 on 2019-05-25 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0017_auto_20190525_0739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='domain',
            field=models.PositiveSmallIntegerField(choices=[(3, 'Rent-a-car/Ride sharing'), (6, 'Sales(Pharma)'), (0, 'Sales'), (1, 'Delivery Service'), (4, 'Insurance'), (2, 'Installation/Maintenance/Repair'), (5, 'Others')], default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(2, 'Employee'), (3, 'Leader'), (0, 'Organizer'), (1, 'Manager')], default=2),
        ),
    ]
