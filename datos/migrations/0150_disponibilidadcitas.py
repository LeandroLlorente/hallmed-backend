# Generated by Django 3.1.2 on 2021-06-16 22:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0149_auto_20210525_1208'),
    ]

    operations = [
        migrations.CreateModel(
            name='DisponibilidadCitas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diaSemana', models.CharField(blank=True, choices=[('LUNES', 'LUNES'), ('MARTES', 'MARTES'), ('MIERCOLES', 'MIERCOLES'), ('JUEVES', 'JUEVES'), ('VIERNES', 'VIERNES'), ('SABADO', 'SABADO'), ('DOMINGO', 'DOMINGO')], default='', max_length=10, null=True)),
                ('inicio', models.TimeField(blank=True, null=True)),
                ('fin', models.TimeField(blank=True, null=True)),
                ('duracion', models.IntegerField(default='', null=True)),
                ('fechaActualizacion', models.DateTimeField(default='', null=True)),
                ('medico', models.ForeignKey(db_column='id_medico', on_delete=django.db.models.deletion.DO_NOTHING, to='datos.medico')),
            ],
        ),
    ]
