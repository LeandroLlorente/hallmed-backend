# Generated by Django 3.1.2 on 2021-01-30 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0105_medicamentorecetado_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='orden',
            name='estado',
            field=models.CharField(choices=[('RESULTADOS', 'RESULTADOS'), ('INDICADO', 'INDICADO')], default='INDICADO', max_length=15),
        ),
    ]
