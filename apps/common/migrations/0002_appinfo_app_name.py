# Generated by Django 2.2 on 2019-06-09 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appinfo',
            name='app_name',
            field=models.CharField(blank=True, default='', max_length=128),
        ),
    ]
