# Generated by Django 2.2 on 2019-04-08 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0003_auto_20190407_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(2, 'Broadcast'), (1, 'Group'), (0, 'Private')], default=0),
        ),
    ]
