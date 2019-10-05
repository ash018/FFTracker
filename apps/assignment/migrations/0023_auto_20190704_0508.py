# Generated by Django 2.2 on 2019-07-04 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignment', '0022_auto_20190619_0449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(4, 'Cancelled'), (1, 'Remaining'), (2, 'In progress'), (3, 'Complete')], default=1),
        ),
    ]
