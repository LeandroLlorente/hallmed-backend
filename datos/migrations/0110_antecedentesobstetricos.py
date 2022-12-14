# Generated by Django 3.1.2 on 2021-02-02 20:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0109_medico_precio'),
    ]

    operations = [
        migrations.CreateModel(
            name='AntecedentesObstetricos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numGestas', models.IntegerField(blank=True, null=True)),
                ('numPartos', models.IntegerField(blank=True, null=True)),
                ('numAbortos', models.IntegerField(blank=True, null=True)),
                ('descPartos', models.CharField(blank=True, max_length=250, null=True)),
                ('descAbortos', models.CharField(blank=True, max_length=250, null=True)),
                ('consulta', models.ForeignKey(db_column='id_consulta', on_delete=django.db.models.deletion.DO_NOTHING, to='datos.consulta')),
            ],
            options={
                'db_table': 'antecedentes_obstetricos',
            },
        ),
    ]
