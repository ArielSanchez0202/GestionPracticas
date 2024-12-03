# Generated by Django 4.1.13 on 2024-12-03 15:32

import coordinador.models
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('reglamento', 'Reglamento Práctica Profesional'), ('inscripcion', 'Ficha de inscripción práctica profesional'), ('avance', 'Informe de avances'), ('autoevaluacion', 'Autoevaluación')], max_length=50)),
                ('archivo', models.FileField(upload_to='documentos_estaticos/')),
                ('descripcion', models.TextField(blank=True, null=True)),
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
            name='FichaInscripcion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('Pendiente', 'Pendiente'), ('Aprobada', 'Aprobada'), ('Rechazada', 'Rechazada'), ('Jefe Carrera', 'Jefe Carrera')], default='Pendiente', max_length=20)),
                ('token', models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ('comentario', models.TextField(blank=True, null=True)),
                ('practica1', models.BooleanField(default=False)),
                ('practica2', models.BooleanField(default=False)),
                ('razon_social', models.CharField(max_length=255)),
                ('direccion_empresa', models.CharField(max_length=255)),
                ('jefe_directo', models.CharField(max_length=255)),
                ('cargo', models.CharField(max_length=100)),
                ('telefono_jefe', models.CharField(max_length=20)),
                ('correo_jefe', models.EmailField(max_length=254)),
                ('fecha_inicio', models.DateField()),
                ('fecha_termino', models.DateField()),
                ('horario_trabajo', models.CharField(max_length=100)),
                ('horario_colacion', models.CharField(max_length=100)),
                ('cargo_desarrollar', models.CharField(max_length=100)),
                ('depto_trabajar', models.CharField(max_length=100)),
                ('actividades_realizar', models.CharField(max_length=100)),
                ('estudiante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordinador.estudiante')),
            ],
        ),
        migrations.CreateModel(
            name='PracticaConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio_limite', models.DateField(default='2024-01-01')),
                ('fecha_termino_limite', models.DateField(default='2024-12-31')),
                ('correo_director', models.EmailField(default='director@example.com', max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Rubrica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_informe', models.CharField(max_length=100)),
                ('portada', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('introduccion', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('objetivo_general', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('objetivos_especificos', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('caracterizacion_empresa', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('datos_supervisor', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('desarrollo_practica', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('recomendaciones', models.CharField(blank=True, choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50, null=True)),
                ('conclusiones', models.CharField(blank=True, choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50, null=True)),
                ('anexos', models.CharField(blank=True, choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50, null=True)),
                ('formato_establecido', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('tercera_persona', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('cita_fuente', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('extension', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('tabla_grafico', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('ortografia', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('cohesion_coherencia', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('ideas_profundizacion', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('roles_impacto', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('riqueza_linguistica', models.CharField(choices=[('Desempeño de excelencia', 'Desempeño de excelencia'), ('Desempeño efectivo', 'Desempeño efectivo'), ('Desempeño que se debe mejorar', 'Desempeño que se debe mejorar'), ('Desempeño insatisfactorio', 'Desempeño insatisfactorio')], max_length=50)),
                ('comentarios', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Practica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('en_progreso', 'En Progreso'), ('rechazada', 'Rechazada'), ('finalizada', 'Finalizada')], default='pendiente', max_length=50)),
                ('fecha_inscripcion', models.DateField(default=datetime.date.today)),
                ('nota', models.DecimalField(decimal_places=1, max_digits=3, null=True)),
                ('estudiante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='practicas', to='coordinador.estudiante')),
            ],
        ),
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mensaje', models.TextField()),
                ('tipo', models.CharField(choices=[('info', 'Información'), ('alerta', 'Alerta'), ('exito', 'Éxito'), ('error', 'Error')], default='info', max_length=10)),
                ('leida', models.BooleanField(default=False)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InformeFinal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True)),
                ('retroalimentacion', models.TextField()),
                ('archivo_informe_final', models.FileField(blank=True, null=True, upload_to='informes_finales/')),
                ('intentos_subida_final', models.PositiveIntegerField(default=0)),
                ('practica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordinador.practica')),
                ('rubrica', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coordinador.rubrica')),
            ],
        ),
        migrations.CreateModel(
            name='InformeConfidencial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.FloatField(default=0)),
                ('calidad_trabajo', models.CharField(choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')], max_length=50)),
                ('calidad_observacion', models.TextField(blank=True, null=True)),
                ('efectividad_trabajo', models.CharField(choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')], max_length=50)),
                ('efectividad_observacion', models.TextField(blank=True, null=True)),
                ('conocimientos_profesionales', models.CharField(choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')], max_length=50)),
                ('conocimientos_observacion', models.TextField(blank=True, null=True)),
                ('adaptabilidad_cambios', models.CharField(choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')], max_length=50)),
                ('adaptabilidad_observacion', models.TextField(blank=True, null=True)),
                ('organizacion_trabajo', models.CharField(choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')], max_length=50)),
                ('organizacion_observacion', models.TextField(blank=True, null=True)),
                ('interes_trabajo', models.CharField(choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')], max_length=50)),
                ('interes_observacion', models.TextField(blank=True, null=True)),
                ('responsabilidad', models.CharField(choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')], max_length=50)),
                ('responsabilidad_observacion', models.TextField(blank=True, null=True)),
                ('cooperacion_trabajo', models.CharField(choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')], max_length=50)),
                ('cooperacion_observacion', models.TextField(blank=True, null=True)),
                ('creatividad', models.CharField(choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')], max_length=50)),
                ('creatividad_observacion', models.TextField(blank=True, null=True)),
                ('iniciativa', models.CharField(choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')], max_length=50)),
                ('iniciativa_observacion', models.TextField(blank=True, null=True)),
                ('integracion_grupo', models.CharField(choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')], max_length=50)),
                ('integracion_observacion', models.TextField(blank=True, null=True)),
                ('positivo_recibir', models.BooleanField()),
                ('tipo_especialidad', models.TextField(blank=True, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('ficha_inscripcion', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='informe_confidencial', to='coordinador.fichainscripcion')),
                ('practica', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coordinador.practica')),
            ],
        ),
        migrations.CreateModel(
            name='InformeAvances',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota_avance', models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True)),
                ('retroalimentacion', models.TextField()),
                ('archivo_informe_avances', models.FileField(blank=True, null=True, upload_to='informes_avances/')),
                ('intentos_subida', models.PositiveIntegerField(default=0)),
                ('practica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordinador.practica')),
                ('rubrica', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coordinador.rubrica')),
            ],
        ),
        migrations.CreateModel(
            name='FormularioToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(default=coordinador.models.generar_token, max_length=64, unique=True)),
                ('enviado', models.BooleanField(default=False)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('ficha_inscripcion', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='formulario_token', to='coordinador.fichainscripcion')),
            ],
        ),
        migrations.AddField(
            model_name='fichainscripcion',
            name='practica',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coordinador.practica'),
        ),
        migrations.CreateModel(
            name='Autoevaluacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.DecimalField(decimal_places=1, max_digits=3, null=True)),
                ('observaciones', models.TextField(null=True)),
                ('pregunta1', models.CharField(choices=[('Siempre', 'Siempre'), ('Frecuentemente', 'Frecuentemente'), ('A veces', 'A veces'), ('Nunca', 'Nunca')], max_length=20)),
                ('pregunta2', models.CharField(choices=[('Siempre', 'Siempre'), ('Frecuentemente', 'Frecuentemente'), ('A veces', 'A veces'), ('Nunca', 'Nunca')], max_length=20)),
                ('pregunta3', models.CharField(choices=[('Siempre', 'Siempre'), ('Frecuentemente', 'Frecuentemente'), ('A veces', 'A veces'), ('Nunca', 'Nunca')], max_length=20)),
                ('pregunta4', models.CharField(choices=[('Siempre', 'Siempre'), ('Frecuentemente', 'Frecuentemente'), ('A veces', 'A veces'), ('Nunca', 'Nunca')], max_length=20)),
                ('pregunta5', models.CharField(choices=[('Siempre', 'Siempre'), ('Frecuentemente', 'Frecuentemente'), ('A veces', 'A veces'), ('Nunca', 'Nunca')], max_length=20)),
                ('pregunta6', models.CharField(choices=[('Siempre', 'Siempre'), ('Frecuentemente', 'Frecuentemente'), ('A veces', 'A veces'), ('Nunca', 'Nunca')], max_length=20)),
                ('pregunta7', models.CharField(choices=[('Siempre', 'Siempre'), ('Frecuentemente', 'Frecuentemente'), ('A veces', 'A veces'), ('Nunca', 'Nunca')], max_length=20)),
                ('pregunta8', models.CharField(choices=[('Siempre', 'Siempre'), ('Frecuentemente', 'Frecuentemente'), ('A veces', 'A veces'), ('Nunca', 'Nunca')], max_length=20)),
                ('pregunta9', models.CharField(choices=[('Siempre', 'Siempre'), ('Frecuentemente', 'Frecuentemente'), ('A veces', 'A veces'), ('Nunca', 'Nunca')], max_length=20)),
                ('pregunta10', models.CharField(choices=[('Siempre', 'Siempre'), ('Frecuentemente', 'Frecuentemente'), ('A veces', 'A veces'), ('Nunca', 'Nunca')], max_length=20)),
                ('pregunta11', models.CharField(choices=[('Siempre', 'Siempre'), ('Frecuentemente', 'Frecuentemente'), ('A veces', 'A veces'), ('Nunca', 'Nunca')], max_length=20)),
                ('comentarios1', models.TextField()),
                ('comentarios2', models.TextField(blank=True, null=True)),
                ('pregunta12', models.CharField(choices=[('Si', 'Sí'), ('No', 'No')], max_length=3)),
                ('comentarios3', models.TextField()),
                ('practica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coordinador.practica')),
            ],
            options={
                'verbose_name': 'Autoevaluación',
                'verbose_name_plural': 'Autoevaluaciones',
            },
        ),
    ]
