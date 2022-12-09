# Generated by Django 3.1.2 on 2020-10-31 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TipoExamen',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('tipo_examen', models.CharField(blank=True, max_length=10, null=True)),
                ('categoria', models.CharField(choices=[('LABORATORIO', 'LABORATORIO'), ('IMAGEN', 'IMAGEN'), ('PROCEDIMIENTO', 'PROCEDIMIENTO')], default='PENDING', max_length=20)),
            ],
            options={
                'db_table': 'tipo_examen',
            },
        ),
    ]
