# Generated by Django 3.1.2 on 2021-01-21 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0097_orden_recomendacion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orden',
            name='recomendacion',
        ),
    ]
