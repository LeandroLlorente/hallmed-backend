# Generated by Django 3.1.2 on 2020-12-07 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0013_auto_20201207_1205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medico',
            name='cod_telefono_pais',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
    ]