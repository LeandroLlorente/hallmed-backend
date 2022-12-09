# Generated by Django 3.1.2 on 2020-12-31 18:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0071_auto_20201230_1500'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrupoExamen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('precio', models.FloatField(blank=True, null=True)),
                ('preparacion', models.CharField(blank=True, max_length=250, null=True)),
                ('entrega', models.CharField(blank=True, max_length=100, null=True)),
                ('referencia', models.CharField(blank=True, max_length=250, null=True)),
                ('examen', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='datos.examen')),
                ('grupo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='datos.unidadmedica')),
            ],
            options={
                'db_table': 'grupo_examen',
            },
        ),
    ]