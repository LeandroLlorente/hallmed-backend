# Generated by Django 3.1.2 on 2020-12-30 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0070_auto_20201230_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sucursalexamen',
            name='precio',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
