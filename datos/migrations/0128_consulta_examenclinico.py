# Generated by Django 3.1.2 on 2021-02-11 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0127_antecedentespediatricos'),
    ]

    operations = [
        migrations.AddField(
            model_name='consulta',
            name='examenClinico',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]