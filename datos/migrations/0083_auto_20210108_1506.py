# Generated by Django 3.1.2 on 2021-01-08 20:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0082_farmacia_medicamento'),
    ]

    operations = [
        migrations.RenameField(
            model_name='medicamento',
            old_name='tipoEspecifico',
            new_name='tipo_especifico',
        ),
        migrations.RenameField(
            model_name='medicamento',
            old_name='TipoGenerico',
            new_name='tipo_generico',
        ),
        migrations.RenameField(
            model_name='medicamento',
            old_name='viaAplicacion',
            new_name='via_aplicacion',
        ),
    ]
