# Generated by Django 3.1.2 on 2020-11-06 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0006_auto_20201105_0849'),
    ]

    operations = [
        migrations.AddField(
            model_name='medico',
            name='activado',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
