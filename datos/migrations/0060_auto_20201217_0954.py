# Generated by Django 3.1.2 on 2020-12-17 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0059_auto_20201217_0931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examen',
            name='examen',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
