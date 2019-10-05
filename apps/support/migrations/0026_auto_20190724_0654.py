# Generated by Django 2.2 on 2019-07-24 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0025_auto_20190717_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersupport',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Pending'), (1, 'In progress'), (2, 'Resolved')], default=0),
        ),
    ]
