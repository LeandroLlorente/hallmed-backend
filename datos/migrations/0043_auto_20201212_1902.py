# Generated by Django 3.1.2 on 2020-12-13 00:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0042_parroquia'),
    ]

    operations = [
        migrations.RenameField(
            model_name='medico',
            old_name='direccion_consultorio',
            new_name='direccion_consultorio1',
        ),
        migrations.RenameField(
            model_name='medico',
            old_name='referencia_consultorio',
            new_name='referencia_consultorio1',
        ),
        migrations.RenameField(
            model_name='medico',
            old_name='telefono_cita',
            new_name='telefono_cita1',
        ),
        migrations.AddField(
            model_name='medico',
            name='canton1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='datos.canton'),
        ),
        migrations.AddField(
            model_name='medico',
            name='parroquia1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='datos.parroquia'),
        ),
        migrations.AddField(
            model_name='medico',
            name='provincia1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='datos.provincia'),
        ),
    ]
