# Generated by Django 3.1.2 on 2021-02-22 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0136_orden_precio_unitario'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultados',
            name='fecha',
            field=models.DateField(auto_now_add=True, db_column='fecha_resultados', null=True),
        ),
    ]