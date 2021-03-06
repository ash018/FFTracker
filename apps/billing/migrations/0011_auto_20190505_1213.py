# Generated by Django 2.2 on 2019-05-05 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0010_auto_20190505_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='bill_type',
            field=models.PositiveSmallIntegerField(choices=[(3, 'Extra tasks'), (1, 'New subscription'), (2, 'New agents')], default=1),
        ),
        migrations.AlterField(
            model_name='payment',
            name='currency',
            field=models.PositiveSmallIntegerField(choices=[(2, 'USD'), (1, 'BDT'), (3, 'EUR')], default=1),
        ),
        migrations.AlterField(
            model_name='payment',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(2, 'Tracking'), (3, 'Full Suite'), (0, 'None'), (1, 'Attendance')], default=0),
        ),
        migrations.AlterField(
            model_name='payment',
            name='state',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Initiated'), (1, 'Created'), (2, 'Successful')], default=0),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='currency',
            field=models.PositiveSmallIntegerField(choices=[(2, 'USD'), (1, 'BDT'), (3, 'EUR')], default=1),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(2, 'Tracking'), (3, 'Full Suite'), (0, 'None'), (1, 'Attendance')], default=0),
        ),
        migrations.AlterField(
            model_name='usage',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(2, 'Tracking'), (3, 'Full Suite'), (0, 'None'), (1, 'Attendance')], default=0),
        ),
        migrations.AlterField(
            model_name='usage',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'active'), (2, 'expired'), (3, 'suspended')], default=1),
        ),
    ]
