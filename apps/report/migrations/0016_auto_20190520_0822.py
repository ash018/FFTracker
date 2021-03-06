# Generated by Django 2.2 on 2019-05-20 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0015_auto_20190516_0613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendanceindividual',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(2, 'Weekend'), (3, 'Holiday'), (1, 'Present'), (4, 'On Leave'), (0, 'Absent')], default=0),
        ),
        migrations.AlterField(
            model_name='ranking',
            name='date_range',
            field=models.PositiveSmallIntegerField(choices=[(3, 'last_week'), (5, 'last_month'), (2, 'this_week'), (1, 'last_day'), (4, 'this_month')], default=2),
        ),
    ]
