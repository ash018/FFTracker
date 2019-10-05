# Generated by Django 2.2 on 2019-04-07 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='bill_type',
            field=models.PositiveSmallIntegerField(choices=[(3, 'Extra tasks'), (1, 'New subscription'), (2, 'New agents')], default=1),
        ),
        migrations.AlterField(
            model_name='payment',
            name='gateway',
            field=models.PositiveSmallIntegerField(choices=[(1, 'BKASH'), (2, 'SSL'), (3, 'IPAY')], default=1),
        ),
        migrations.AlterField(
            model_name='payment',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(3, 'Full Suite'), (1, 'Attendance'), (2, 'Tracking'), (0, 'None')], default=0),
        ),
        migrations.AlterField(
            model_name='payment',
            name='state',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Initiated'), (1, 'Created'), (2, 'Successful')], default=0),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(3, 'Full Suite'), (1, 'Attendance'), (2, 'Tracking'), (0, 'None')], default=0),
        ),
        migrations.AlterField(
            model_name='usage',
            name='package',
            field=models.PositiveSmallIntegerField(choices=[(3, 'Full Suite'), (1, 'Attendance'), (2, 'Tracking'), (0, 'None')], default=0),
        ),
        migrations.AlterField(
            model_name='usage',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(2, 'expired'), (1, 'active'), (3, 'suspended')], default=1),
        ),
    ]
