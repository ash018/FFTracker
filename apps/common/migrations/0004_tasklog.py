# Generated by Django 2.2 on 2019-06-19 04:49

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_auto_20190609_1050'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.CharField(blank=True, default='', max_length=64)),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('message', models.TextField(blank=True, default='')),
                ('status', models.PositiveIntegerField(choices=[(0, 'started'), (1, 'finished'), (2, 'failed')], default=0)),
            ],
        ),
    ]
