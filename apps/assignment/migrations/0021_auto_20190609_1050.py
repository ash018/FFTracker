# Generated by Django 2.2 on 2019-06-09 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0020_auto_20190609_0939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(4, 'Cancelled'), (1, 'Remaining'), (3, 'Complete'), (2, 'In progress')], default=1),
        ),
    ]
