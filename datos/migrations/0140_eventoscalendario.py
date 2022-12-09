# Generated by Django 3.1.2 on 2021-05-11 13:00

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0139_medicoseguro'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventosCalendario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(blank=True, max_length=500, null=True)),
                ('inicio', models.DateField(default=datetime.date.today, verbose_name='inicio')),
                ('fin', models.DateField(default=datetime.date.today, verbose_name='fin')),
                ('estado', models.CharField(blank=True, choices=[('AGENDADO', 'AGENDADO'), ('REALIZADO', 'REALIZADO'), ('CANCELADO', 'CANCELADO')], default='', max_length=50, null=True)),
                ('consulta', models.ForeignKey(db_column='id_consulta', on_delete=django.db.models.deletion.DO_NOTHING, to='datos.consulta')),
                ('paciente', models.ForeignKey(blank=True, db_column='id_paciente', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='datos.paciente')),
            ],
        ),
    ]