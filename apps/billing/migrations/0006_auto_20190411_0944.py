# Generated by Django 2.2 on 2019-04-11 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0005_auto_20190408_0925'),
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
            field=models.PositiveSmallIntegerField(choices=[(0, 'None'), (3, 'Full Suite'), (1, 'Attendance'), (2, 'Tracking')], default=0),
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
            field=models.PositiveSmallIntegerField(choices=[(0, 'None'), (3, 'Full Suite'), (1, 'Attendance'), (2, 'Tracking')], default=0),
        ),
        migrations.AlterField(
            model_name='usage',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(0, 'None'), (3, 'Full Suite'), (1, 'Attendance'), (2, 'Tracking')], default=0),
        ),
        migrations.AlterField(
            model_name='usage',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(2, 'expired'), (3, 'suspended'), (1, 'active')], default=1),
        ),
    ]
