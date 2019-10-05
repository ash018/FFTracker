# Generated by Django 2.2 on 2019-04-07 03:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('task', '0001_initial'),
        ('state', '0001_initial'),
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstate',
            name='active_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='task.Task'),
        ),
        migrations.AddField(
            model_name='userstate',
            name='last_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='location.Location'),
        ),
    ]
