# Generated by Django 4.1.13 on 2024-12-02 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinador', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='practicaconfig',
            name='correo_director',
            field=models.EmailField(default='director@example.com', max_length=254),
        ),
        migrations.AlterField(
            model_name='document',
            name='tipo',
            field=models.CharField(choices=[('reglamento', 'Reglamento Práctica Profesional'), ('inscripcion', 'Ficha de inscripción práctica profesional'), ('avance', 'Informe de avances'), ('autoevaluacion', 'Autoevaluación')], max_length=50),
        ),
    ]