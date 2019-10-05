# Generated by Django 2.2 on 2019-04-08 06:46

import apps.org.config
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('org', '0003_auto_20190408_0518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='weekend',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(choices=[(5, 'Sat'), (0, 'Mon'), (3, 'Thu'), (1, 'Tue'), (2, 'wed'), (4, 'Fri'), (6, 'Sun')]), blank=True, default=apps.org.config.default_weekend, size=None),
        ),
    ]
