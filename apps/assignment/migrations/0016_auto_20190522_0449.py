# Generated by Django 2.2 on 2019-05-22 04:49

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0015_assignment_assignee_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='checklist',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='custom_fields',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(4, 'Cancelled'), (1, 'Remaining'), (3, 'Complete'), (2, 'In progress')], default=1),
        ),
    ]
