# Generated by Django 3.1.2 on 2021-01-05 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0077_orden'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consulta',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False),
        ),
    ]
