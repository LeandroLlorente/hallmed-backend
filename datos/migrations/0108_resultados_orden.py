# Generated by Django 3.1.2 on 2021-01-31 02:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0107_resultados'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultados',
            name='orden',
            field=models.ForeignKey(blank=True, db_column='id_orden', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='datos.orden'),
        ),
    ]
