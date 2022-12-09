# Generated by Django 3.1.2 on 2020-12-12 15:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0038_canton'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parroquia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parroquia', models.CharField(blank=True, max_length=60, null=True)),
                ('canton', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='datos.canton')),
            ],
            options={
                'db_table': 'parroquia',
            },
        ),
    ]