# Generated by Django 2.2 on 2019-05-20 08:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assignment', '0014_auto_20190516_0613'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='assignee_list',
            field=models.ManyToManyField(blank=True, related_name='user_assignees', to=settings.AUTH_USER_MODEL),
        ),
    ]
