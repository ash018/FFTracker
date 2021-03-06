# Generated by Django 2.2 on 2019-05-20 08:22

import apps.org.config
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org', '0013_auto_20190516_0613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='weekend',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(choices=[(1, 'Tue'), (4, 'Fri'), (5, 'Sat'), (3, 'Thu'), (6, 'Sun'), (0, 'Mon'), (2, 'wed')]), blank=True, default=apps.org.config.default_weekend, size=None),
        ),
    ]
