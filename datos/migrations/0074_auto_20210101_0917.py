# Generated by Django 3.1.2 on 2021-01-01 14:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0073_consulta'),
    ]

    operations = [
        migrations.RenameField(
            model_name='consulta',
            old_name='id_diagnostico',
            new_name='diagnostico',
        ),
        migrations.RenameField(
            model_name='consulta',
            old_name='id_medico',
            new_name='medico',
        ),
        migrations.RenameField(
            model_name='consulta',
            old_name='id_paciente',
            new_name='paciente',
        ),
    ]
