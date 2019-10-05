# Generated by Django 2.2 on 2019-05-25 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0018_auto_20190525_0739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersupport',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(2, 'Resolved'), (1, 'In progress'), (0, 'Pending')], default=0),
        ),
    ]
