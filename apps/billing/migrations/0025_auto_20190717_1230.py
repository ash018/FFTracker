# Generated by Django 2.2 on 2019-07-17 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0024_auto_20190704_0508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='bill_type',
            field=models.PositiveSmallIntegerField(choices=[(2, 'New agents'), (3, 'Extra tasks'), (1, 'New subscription')], default=1),
        ),
        migrations.AlterField(
            model_name='payment',
            name='currency',
            field=models.PositiveSmallIntegerField(choices=[(1, 'BDT'), (3, 'EUR'), (2, 'USD')], default=1),
        ),
        migrations.AlterField(
            model_name='payment',
            name='gateway',
            field=models.PositiveSmallIntegerField(choices=[(3, 'IPAY'), (1, 'BKASH'), (2, 'SSL')], default=1),
        ),
        migrations.AlterField(
            model_name='payment',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(0, 'None'), (2, 'Tracking'), (3, 'Full Suite'), (1, 'Attendance'), (4, 'Task Management')], default=0),
        ),
        migrations.AlterField(
            model_name='payment',
            name='state',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Initiated'), (2, 'Successful'), (1, 'Created')], default=0),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='currency',
            field=models.PositiveSmallIntegerField(choices=[(1, 'BDT'), (3, 'EUR'), (2, 'USD')], default=1),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(0, 'None'), (2, 'Tracking'), (3, 'Full Suite'), (1, 'Attendance'), (4, 'Task Management')], default=0),
        ),
        migrations.AlterField(
            model_name='usage',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(0, 'None'), (2, 'Tracking'), (3, 'Full Suite'), (1, 'Attendance'), (4, 'Task Management')], default=0),
        ),
    ]
