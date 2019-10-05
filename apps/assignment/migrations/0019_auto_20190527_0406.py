# Generated by Django 2.2 on 2019-05-27 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0018_auto_20190525_0739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(4, 'Cancelled'), (2, 'In progress'), (3, 'Complete'), (1, 'Remaining')], default=1),
        ),
    ]
