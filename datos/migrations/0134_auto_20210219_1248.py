# Generated by Django 3.1.2 on 2021-02-19 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0133_sucursal_compensacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sucursal',
            name='compensacion',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]