# Generated by Django 2.2 on 2019-06-09 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0016_auto_20190525_0934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(2, 'Broadcast'), (1, 'Group'), (0, 'Private')], default=0),
        ),
    ]
