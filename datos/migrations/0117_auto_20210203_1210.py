# Generated by Django 3.1.2 on 2021-02-03 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0116_ratingmedico_consulta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ratingmedico',
            name='rating',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
