# Generated by Django 3.1.2 on 2021-05-22 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0144_auto_20210522_1225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventoscalendario',
            name='consulta',
            field=models.ForeignKey(blank=True, db_column='id_consulta', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='datos.consulta'),
        ),
    ]
