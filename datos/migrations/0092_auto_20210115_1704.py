# Generated by Django 3.1.2 on 2021-01-15 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0091_auto_20210113_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicamentofarmacia',
            name='descripcion',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='medicamentofarmacia',
            name='precio',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
