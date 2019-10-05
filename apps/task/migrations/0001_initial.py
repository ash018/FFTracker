# Generated by Django 2.2 on 2019-04-07 03:10

import apps.task.config
import datetime
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('org', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('title', models.CharField(max_length=128)),
                ('status', models.PositiveSmallIntegerField(choices=[(4, 'Cancelled'), (2, 'In progress'), (3, 'Complete'), (0, 'Unassigned'), (5, 'Postponed'), (1, 'Remaining')], default=0)),
                ('start', models.DateTimeField(default=django.utils.timezone.now)),
                ('deadline', models.DateTimeField(default=apps.task.config.default_duration)),
                ('images', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('ts_start', models.DateTimeField(blank=True, null=True)),
                ('ts_finish', models.DateTimeField(blank=True, null=True)),
                ('delayed', models.BooleanField(default=False)),
                ('task_type', models.CharField(max_length=128)),
                ('point_start', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('point_finish', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('point', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('address', models.TextField(blank=True)),
                ('image_required', models.BooleanField(default=False)),
                ('attachment_required', models.BooleanField(default=False)),
                ('custom_fields', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TaskTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_type', models.CharField(max_length=128)),
                ('task_fields', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('org', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='org.Organization')),
            ],
        ),
    ]
