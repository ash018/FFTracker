# Generated by Django 2.2 on 2019-05-27 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0018_auto_20190525_0934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datausage',
            name='mac',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AlterField(
            model_name='user',
            name='domain',
            field=models.PositiveSmallIntegerField(choices=[(5, 'Others'), (6, 'Sales(Pharma)'), (2, 'Installation/Maintenance/Repair'), (4, 'Insurance'), (1, 'Delivery Service'), (3, 'Rent-a-car/Ride sharing'), (0, 'Sales')], default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(2, 'Employee'), (1, 'Manager'), (3, 'Leader'), (0, 'Organizer')], default=2),
        ),
    ]
