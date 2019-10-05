# Generated by Django 2.2 on 2019-05-22 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0015_auto_20190520_0822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersupport',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Pending'), (2, 'Resolved'), (1, 'In progress')], default=0),
        ),
    ]
