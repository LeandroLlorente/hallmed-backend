# Generated by Django 3.1.2 on 2020-12-22 17:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('datos', '0063_auto_20201221_0711'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sucursal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('lat', models.CharField(blank=True, max_length=10, null=True)),
                ('lon', models.CharField(blank=True, max_length=10, null=True)),
                ('slogan', models.CharField(blank=True, max_length=50, null=True)),
                ('quienes_somos', models.CharField(blank=True, max_length=250, null=True)),
                ('direccion', models.CharField(blank=True, max_length=100, null=True)),
                ('referencia_direccion', models.CharField(blank=True, max_length=150, null=True)),
                ('direccionmatriz', models.CharField(blank=True, max_length=100, null=True)),
                ('telefono', models.CharField(blank=True, max_length=30, null=True)),
                ('telefono_whatsapp', models.CharField(blank=True, max_length=15, null=True)),
                ('facebook', models.CharField(blank=True, max_length=100, null=True)),
                ('twitter', models.CharField(blank=True, max_length=100, null=True)),
                ('pag_web', models.CharField(blank=True, max_length=100, null=True)),
                ('horario_atencion', models.CharField(blank=True, max_length=100, null=True)),
                ('activado', models.BooleanField(blank=True, null=True)),
                ('canton', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='canton_sucursal', to='datos.canton')),
                ('parroquia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parroquia_sucursal', to='datos.parroquia')),
                ('provincia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='provincia_sucursal', to='datos.provincia')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sucursal',
            },
        ),
    ]