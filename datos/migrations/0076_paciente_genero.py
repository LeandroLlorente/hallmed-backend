# Generated by Django 3.1.2 on 2021-01-03 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0075_auto_20210101_1022'),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='genero',
            field=models.CharField(choices=[('MASCULINO', 'MASCULINO'), ('FEMENINO', 'FEMENINO')], default='', max_length=10),
        ),
    ]
