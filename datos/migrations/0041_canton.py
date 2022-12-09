# Generated by Django 3.1.2 on 2020-12-12 16:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0040_auto_20201212_1050'),
    ]

    operations = [
        migrations.CreateModel(
            name='Canton',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('canton', models.CharField(blank=True, max_length=40, null=True)),
                ('provincia', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='datos.provincia')),
            ],
            options={
                'db_table': 'canton',
            },
        ),
    ]
