# Generated by Django 3.1.2 on 2021-05-22 16:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0142_auto_20210522_0841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventoscalendario',
            name='inicio',
            field=models.DateTimeField(default=datetime.date.today, verbose_name='inicio'),
        ),
    ]