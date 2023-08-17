# Generated by Django 4.2.3 on 2023-08-04 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Padron',
            fields=[
                ('ruc', models.CharField(max_length=11, primary_key=True, serialize=False, unique=True)),
                ('razon_social', models.CharField(blank=True, max_length=255, null=True)),
                ('estado', models.CharField(blank=True, max_length=255, null=True)),
                ('condicion', models.CharField(blank=True, max_length=255, null=True)),
                ('tipo_contribuyente', models.CharField(blank=True, max_length=255, null=True)),
                ('ubigeo', models.CharField(blank=True, max_length=20, null=True)),
                ('departamento', models.CharField(blank=True, max_length=50, null=True)),
                ('provincia', models.CharField(blank=True, max_length=50, null=True)),
                ('distrito', models.CharField(blank=True, max_length=50, null=True)),
                ('domicilio_fiscal', models.TextField(blank=True, null=True)),
                ('ciiu_v3_principal', models.CharField(blank=True, max_length=200, null=True)),
                ('ciiu_v3_secundario', models.CharField(blank=True, max_length=200, null=True)),
                ('ciiu_v4_principal', models.CharField(blank=True, max_length=200, null=True)),
                ('numero_empleados', models.IntegerField(blank=True, null=True)),
                ('tipo_facturacion', models.CharField(blank=True, max_length=50, null=True)),
                ('tipo_contabilidad', models.CharField(blank=True, max_length=50, null=True)),
                ('comercio_exterior', models.CharField(blank=True, max_length=50, null=True)),
                ('ultima_actualizacion', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Padron',
                'verbose_name_plural': 'Padrones',
                'indexes': [models.Index(fields=['razon_social'], name='sunat_padro_razon_s_d9afed_idx')],
            },
        ),
    ]
