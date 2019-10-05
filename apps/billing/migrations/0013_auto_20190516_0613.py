# Generated by Django 2.2 on 2019-05-16 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0012_auto_20190513_0517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='currency',
            field=models.PositiveSmallIntegerField(choices=[(1, 'BDT'), (2, 'USD'), (3, 'EUR')], default=1),
        ),
        migrations.AlterField(
            model_name='payment',
            name='gateway',
            field=models.PositiveSmallIntegerField(choices=[(3, 'IPAY'), (2, 'SSL'), (1, 'BKASH')], default=1),
        ),
        migrations.AlterField(
            model_name='payment',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(3, 'Full Suite'), (2, 'Tracking'), (1, 'Attendance'), (0, 'None'), (4, 'Task Management')], default=0),
        ),
        migrations.AlterField(
            model_name='payment',
            name='state',
            field=models.PositiveSmallIntegerField(choices=[(2, 'Successful'), (0, 'Initiated'), (1, 'Created')], default=0),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='currency',
            field=models.PositiveSmallIntegerField(choices=[(1, 'BDT'), (2, 'USD'), (3, 'EUR')], default=1),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(3, 'Full Suite'), (2, 'Tracking'), (1, 'Attendance'), (0, 'None'), (4, 'Task Management')], default=0),
        ),
        migrations.AlterField(
            model_name='usage',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(3, 'Full Suite'), (2, 'Tracking'), (1, 'Attendance'), (0, 'None'), (4, 'Task Management')], default=0),
        ),
        migrations.AlterField(
            model_name='usage',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(2, 'expired'), (1, 'active'), (3, 'suspended')], default=1),
        ),
    ]
