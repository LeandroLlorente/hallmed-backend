# Generated by Django 3.1.2 on 2021-01-12 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0088_auto_20210110_1745'),
    ]

    operations = [
        migrations.AddField(
            model_name='consulta',
            name='tipo_diagnostico',
            field=models.CharField(choices=[('PRESUNTIVO', 'PRESUNTIVO'), ('DEFINITIVO', 'DEFINITIVO')], default='', max_length=50),
        ),
    ]
