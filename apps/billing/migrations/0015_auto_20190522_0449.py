# Generated by Django 2.2 on 2019-05-22 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0014_auto_20190520_0822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='bill_type',
            field=models.PositiveSmallIntegerField(choices=[(2, 'New agents'), (1, 'New subscription'), (3, 'Extra tasks')], default=1),
        ),
        migrations.AlterField(
            model_name='payment',
            name='currency',
            field=models.PositiveSmallIntegerField(choices=[(2, 'USD'), (3, 'EUR'), (1, 'BDT')], default=1),
        ),
        migrations.AlterField(
            model_name='payment',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(0, 'None'), (2, 'Tracking'), (3, 'Full Suite'), (4, 'Task Management'), (1, 'Attendance')], default=0),
        ),
        migrations.AlterField(
            model_name='payment',
            name='state',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Initiated'), (2, 'Successful'), (1, 'Created')], default=0),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='currency',
            field=models.PositiveSmallIntegerField(choices=[(2, 'USD'), (3, 'EUR'), (1, 'BDT')], default=1),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(0, 'None'), (2, 'Tracking'), (3, 'Full Suite'), (4, 'Task Management'), (1, 'Attendance')], default=0),
        ),
        migrations.AlterField(
            model_name='usage',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(0, 'None'), (2, 'Tracking'), (3, 'Full Suite'), (4, 'Task Management'), (1, 'Attendance')], default=0),
        ),
        migrations.AlterField(
            model_name='usage',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(3, 'suspended'), (1, 'active'), (2, 'expired')], default=1),
        ),
    ]
