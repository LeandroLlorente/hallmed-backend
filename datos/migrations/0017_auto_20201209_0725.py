# Generated by Django 3.1.2 on 2020-12-09 12:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0016_auto_20201209_0621'),
    ]

    operations = [
        migrations.RenameField(
            model_name='unidadmedica',
            old_name='activo',
            new_name='activado',
        ),
    ]
