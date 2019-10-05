# Generated by Django 2.2 on 2019-06-09 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0019_auto_20190527_0406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Remaining'), (4, 'Cancelled'), (3, 'Complete'), (2, 'In progress')], default=1),
        ),
    ]
