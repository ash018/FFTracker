# Generated by Django 2.2 on 2019-06-09 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0020_auto_20190609_0939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersupport',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Pending'), (1, 'In progress'), (2, 'Resolved')], default=0),
        ),
    ]
