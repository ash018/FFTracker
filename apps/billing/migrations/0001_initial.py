# Generated by Django 2.2 on 2019-04-07 03:10

import apps.billing.models
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
            name='Usage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('init_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('exp_date', models.DateTimeField(default=apps.billing.models.default_cycle)),
                ('consumed_tasks', models.PositiveIntegerField(default=0)),
                ('bill_subscription', models.FloatField(default=0.0)),
                ('bill_new_agent', models.FloatField(default=0.0)),
                ('bill_extra_task', models.FloatField(default=0.0)),
                ('package', models.PositiveSmallIntegerField(choices=[(0, 'None'), (3, 'Full Suite'), (2, 'Tracking'), (1, 'Attendance')], default=0)),
                ('discount', models.FloatField(default=0.0)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'active'), (2, 'expired'), (3, 'suspended')], default=1)),
                ('org', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='org.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('agent_limit', models.PositiveIntegerField(default=10)),
                ('added_agents', models.PositiveIntegerField(default=0)),
                ('task_limit', models.PositiveIntegerField(default=1500)),
                ('currency', models.PositiveSmallIntegerField(choices=[(2, 'USD'), (1, 'BDT'), (3, 'EUR')], default=1)),
                ('package', models.PositiveSmallIntegerField(choices=[(0, 'None'), (3, 'Full Suite'), (2, 'Tracking'), (1, 'Attendance')], default=0)),
                ('_is_premium', models.BooleanField(default=False)),
                ('_is_trial', models.BooleanField(default=False)),
                ('_next_due', models.FloatField(default=0.0)),
                ('renew_needed', models.BooleanField(default=False)),
                ('current_usage', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='billing.Usage')),
                ('org', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='org.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gateway', models.PositiveSmallIntegerField(choices=[(2, 'SSL'), (1, 'BKASH'), (3, 'IPAY')], default=1)),
                ('vendor_uid', models.CharField(max_length=255, unique=True)),
                ('payment_uid', models.CharField(max_length=255, null=True)),
                ('state', models.PositiveSmallIntegerField(choices=[(0, 'Initiated'), (2, 'Successful'), (1, 'Created')], default=0)),
                ('amount', models.FloatField(default=0.0)),
                ('package', models.PositiveSmallIntegerField(choices=[(0, 'None'), (3, 'Full Suite'), (2, 'Tracking'), (1, 'Attendance')], default=0)),
                ('bill_type', models.PositiveSmallIntegerField(choices=[(3, 'Extra tasks'), (2, 'New agents'), (1, 'New subscription')], default=1)),
                ('extra_tasks', models.PositiveIntegerField(default=0)),
                ('new_agents', models.PositiveIntegerField(default=0)),
                ('details', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('currency', models.PositiveSmallIntegerField(choices=[(2, 'USD'), (1, 'BDT'), (3, 'EUR')], default=1)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('subscription', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='billing.Subscription')),
            ],
        ),
    ]
