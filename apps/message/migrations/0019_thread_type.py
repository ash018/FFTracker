# Generated by Django 2.2 on 2019-06-09 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0018_auto_20190609_0954'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(2, 'Broadcast'), (0, 'Private'), (1, 'Group')], default=0),
        ),
    ]
