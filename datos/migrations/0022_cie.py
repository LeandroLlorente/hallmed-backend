# Generated by Django 3.1.2 on 2020-12-11 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datos', '0021_auto_20201211_1359'),
    ]

    operations = [
        migrations.CreateModel(
            name='CIE',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('cie', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'db_table': 'cie',
            },
        ),
    ]
