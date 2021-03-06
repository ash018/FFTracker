# Generated by Django 2.2 on 2019-04-07 03:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('task', '0001_initial'),
        ('org', '0001_initial'),
        ('report', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskcombined',
            name='cancelled',
            field=models.ManyToManyField(blank=True, related_name='task_cancelled', to='task.Task'),
        ),
        migrations.AddField(
            model_name='taskcombined',
            name='complete',
            field=models.ManyToManyField(blank=True, related_name='task_complete', to='task.Task'),
        ),
        migrations.AddField(
            model_name='taskcombined',
            name='delayed',
            field=models.ManyToManyField(blank=True, related_name='task_delayed', to='task.Task'),
        ),
        migrations.AddField(
            model_name='taskcombined',
            name='org',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='org.Organization'),
        ),
        migrations.AddField(
            model_name='taskcombined',
            name='postponed',
            field=models.ManyToManyField(blank=True, related_name='task_postponed', to='task.Task'),
        ),
        migrations.AddField(
            model_name='ranking',
            name='org',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='org.Organization'),
        ),
    ]
