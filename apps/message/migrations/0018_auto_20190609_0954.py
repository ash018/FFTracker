# Generated by Django 2.2 on 2019-06-09 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0017_auto_20190609_0939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(2, 'Broadcast'), (0, 'Private'), (1, 'Group')], default=0),
        ),
    ]
