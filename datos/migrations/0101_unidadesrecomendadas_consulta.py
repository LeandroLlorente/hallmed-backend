# Generated by Django 3.1.2 on 2021-01-21 13:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0100_auto_20210121_0802'),
    ]

    operations = [
        migrations.AddField(
            model_name='unidadesrecomendadas',
            name='consulta',
            field=models.ForeignKey(blank=True, db_column='id_consulta', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='datos.consulta'),
        ),
    ]
