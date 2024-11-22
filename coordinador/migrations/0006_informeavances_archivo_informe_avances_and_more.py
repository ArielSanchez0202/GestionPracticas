# Generated by Django 5.0.6 on 2024-11-22 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinador', '0005_alter_fichainscripcion_practica'),
    ]

    operations = [
        migrations.AddField(
            model_name='informeavances',
            name='archivo_informe_avances',
            field=models.FileField(blank=True, null=True, upload_to='informes_avances/'),
        ),
        migrations.AddField(
            model_name='informeavances',
            name='intentos_subida',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='informefinal',
            name='archivo_informe_final',
            field=models.FileField(blank=True, null=True, upload_to='informes_finales/'),
        ),
        migrations.AddField(
            model_name='informefinal',
            name='intentos_subida_final',
            field=models.PositiveIntegerField(default=0),
        ),
    ]