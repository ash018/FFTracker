# Generated by Django 2.2 on 2019-06-19 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0024_auto_20190609_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendanceindividual',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Present'), (3, 'Holiday'), (2, 'Weekend'), (4, 'On Leave'), (0, 'Absent')], default=0),
        ),
        migrations.AlterField(
            model_name='ranking',
            name='date_range',
            field=models.PositiveSmallIntegerField(choices=[(5, 'last_month'), (3, 'last_week'), (2, 'this_week'), (1, 'last_day'), (4, 'this_month')], default=2),
        ),
    ]
