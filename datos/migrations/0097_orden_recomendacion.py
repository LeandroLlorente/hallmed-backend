# Generated by Django 3.1.2 on 2021-01-21 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0096_orden_precio_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='orden',
            name='recomendacion',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]