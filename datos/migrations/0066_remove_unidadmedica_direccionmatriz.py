# Generated by Django 3.1.2 on 2020-12-22 17:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0065_remove_sucursal_direccionmatriz'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unidadmedica',
            name='direccionmatriz',
        ),
    ]