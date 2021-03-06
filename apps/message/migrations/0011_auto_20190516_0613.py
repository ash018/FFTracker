# Generated by Django 2.2 on 2019-05-16 06:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0010_auto_20190513_0517'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='last_message_time',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='message',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Private'), (1, 'Group'), (2, 'Broadcast')], default=0),
        ),
    ]
