# Generated by Django 5.0.6 on 2024-11-21 23:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinador', '0004_fichainscripcion_practica'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fichainscripcion',
            name='practica',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coordinador.practica'),
        ),
    ]
