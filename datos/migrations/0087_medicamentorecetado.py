# Generated by Django 3.1.2 on 2021-01-10 22:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0086_auto_20210110_0947'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicamentoRecetado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dosis', models.CharField(blank=True, max_length=50, null=True)),
                ('frecuencia', models.CharField(blank=True, max_length=50, null=True)),
                ('duracion', models.CharField(blank=True, max_length=50, null=True)),
                ('consulta', models.ForeignKey(db_column='id_consulta', on_delete=django.db.models.deletion.DO_NOTHING, to='datos.consulta')),
                ('medicamento', models.ForeignKey(db_column='id_medicamento', on_delete=django.db.models.deletion.DO_NOTHING, to='datos.medicamento')),
            ],
        ),
    ]
