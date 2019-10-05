# Generated by Django 2.2 on 2019-06-19 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0019_thread_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Private'), (1, 'Group'), (2, 'Broadcast')], default=0),
        ),
        migrations.AlterField(
            model_name='thread',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Private'), (1, 'Group'), (2, 'Broadcast')], default=0),
        ),
    ]
