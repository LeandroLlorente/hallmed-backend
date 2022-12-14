# Generated by Django 3.1.2 on 2020-12-06 20:05

import datos.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0009_medico_regacess'),
    ]

    operations = [
        migrations.RenameField(
            model_name='medico',
            old_name='codigoMedico',
            new_name='cedula',
        ),
        migrations.AlterField(
            model_name='medico',
            name='regAcess',
            field=models.FileField(null=True, upload_to=datos.models.user_directory_path_acess),
        ),
        migrations.AlterField(
            model_name='medico',
            name='regSene',
            field=models.FileField(null=True, upload_to=datos.models.user_directory_path_sene),
        ),
    ]
