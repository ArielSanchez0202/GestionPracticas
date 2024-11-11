# Generated by Django 4.1.13 on 2024-11-10 18:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coordinador',
            fields=[
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('rut', models.CharField(max_length=20, unique=True)),
                ('domicilio', models.CharField(max_length=255)),
                ('carrera', models.CharField(max_length=100)),
                ('numero_telefono', models.CharField(max_length=20)),
                ('first_login', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Estudiante',
            fields=[
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('rut', models.CharField(max_length=20, unique=True)),
                ('domicilio', models.CharField(max_length=255)),
                ('carrera', models.CharField(max_length=100)),
                ('numero_telefono', models.CharField(max_length=20)),
                ('first_login', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rubrica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_informe', models.CharField(max_length=100)),
                ('criterio1', models.CharField(max_length=100)),
                ('criterio2', models.CharField(max_length=100)),
                ('ponderacion_criterio1', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='Practica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('en_progreso', 'En Progreso'), ('finalizada', 'Finalizada')], default='pendiente', max_length=50)),
                ('fecha_inscripcion', models.DateField()),
                ('estudiante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='practicas', to='coordinador.estudiante')),
            ],
        ),
        migrations.CreateModel(
            name='InformeFinal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.DecimalField(decimal_places=1, max_digits=3)),
                ('retroalimentacion', models.TextField()),
                ('practica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordinador.practica')),
                ('rubrica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordinador.rubrica')),
            ],
        ),
        migrations.CreateModel(
            name='InformeConfidencial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comentario', models.TextField()),
                ('practica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordinador.practica')),
                ('rubrica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordinador.rubrica')),
            ],
        ),
        migrations.CreateModel(
            name='InformeAvances',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota_avance', models.DecimalField(decimal_places=1, max_digits=3)),
                ('retroalimentacion', models.TextField()),
                ('practica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordinador.practica')),
                ('rubrica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordinador.rubrica')),
            ],
        ),
        migrations.CreateModel(
            name='FichaInscripcion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('empresa', models.CharField(max_length=255)),
                ('supervisor', models.CharField(max_length=255)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('practica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordinador.practica')),
            ],
        ),
        migrations.CreateModel(
            name='Autoevaluacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.DecimalField(decimal_places=1, max_digits=3)),
                ('observaciones', models.TextField()),
                ('practica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordinador.practica')),
            ],
        ),
    ]
