# Generated by Django 2.2 on 2019-05-20 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0013_auto_20190516_0613'),
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
            model_name='subscription',
            name='currency',
            field=models.PositiveSmallIntegerField(choices=[(1, 'BDT'), (3, 'EUR'), (2, 'USD')], default=1),
        ),
        migrations.AlterField(
            model_name='usage',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(2, 'expired'), (3, 'suspended'), (1, 'active')], default=1),
        ),
    ]
