# Generated by Django 2.2 on 2019-05-22 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0016_auto_20190522_0449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersupport',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'In progress'), (0, 'Pending'), (2, 'Resolved')], default=0),
        ),
    ]
