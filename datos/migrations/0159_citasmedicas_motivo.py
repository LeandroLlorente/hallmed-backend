# Generated by Django 3.1.2 on 2021-09-21 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0158_intervalosdisponibilidad_activo'),
    ]

    operations = [
        migrations.AddField(
            model_name='citasmedicas',
            name='motivo',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
