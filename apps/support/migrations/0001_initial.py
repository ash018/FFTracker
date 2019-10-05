# Generated by Django 2.2 on 2019-04-07 03:10

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('org', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerSupport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.PositiveSmallIntegerField(choices=[(2, 'Resolved'), (0, 'Pending'), (1, 'In progress')], default=0)),
                ('org', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='org.Organization')),
            ],
        ),
    ]
