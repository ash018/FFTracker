# Generated by Django 2.2 on 2019-04-08 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_auto_20190408_0518'),
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
            field=models.PositiveSmallIntegerField(choices=[(2, 'SSL'), (3, 'IPAY'), (1, 'BKASH')], default=1),
        ),
        migrations.AlterField(
            model_name='payment',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(0, 'None'), (1, 'Attendance'), (2, 'Tracking'), (3, 'Full Suite')], default=0),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='currency',
            field=models.PositiveSmallIntegerField(choices=[(1, 'BDT'), (3, 'EUR'), (2, 'USD')], default=1),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(0, 'None'), (1, 'Attendance'), (2, 'Tracking'), (3, 'Full Suite')], default=0),
        ),
        migrations.AlterField(
            model_name='usage',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(0, 'None'), (1, 'Attendance'), (2, 'Tracking'), (3, 'Full Suite')], default=0),
        ),
        migrations.AlterField(
            model_name='usage',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'active'), (3, 'suspended'), (2, 'expired')], default=1),
        ),
    ]
