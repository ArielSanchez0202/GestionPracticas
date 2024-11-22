# Generated by Django 5.0.6 on 2024-11-22 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinador', '0006_informeavances_archivo_informe_avances_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fichainscripcion',
            name='estado',
            field=models.CharField(choices=[('Pendiente', 'Pendiente'), ('Aprobada', 'Aprobada'), ('Rechazada', 'Rechazada')], default='Pendiente', max_length=10),
        ),
    ]
