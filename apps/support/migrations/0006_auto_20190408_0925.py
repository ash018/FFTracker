# Generated by Django 2.2 on 2019-04-08 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0005_auto_20190408_0646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customersupport',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(2, 'Resolved'), (1, 'In progress'), (0, 'Pending')], default=0),
        ),
    ]
