from django.db import models
from django.contrib.auth.models import User  # Importa el modelo de usuario de Django
import uuid

# Modelo Coordinador
class Coordinador(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    rut = models.CharField(max_length=20, unique=True)
    domicilio = models.CharField(max_length=255)
    carrera = models.CharField(max_length=100)
    numero_telefono = models.CharField(max_length=20)
    first_login = models.BooleanField(default=True)

    def __str__(self):
        return f'Coordinador: {self.usuario.first_name} {self.usuario.last_name}'

# Modelo Estudiante
class Estudiante(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    rut = models.CharField(max_length=20, unique=True)
    domicilio = models.CharField(max_length=255)
    carrera = models.CharField(max_length=100)
    numero_telefono = models.CharField(max_length=20)  # Campo agregado para el número de teléfono
    first_login = models.BooleanField(default=True)

    def __str__(self):
        return f'Estudiante: {self.usuario.first_name} {self.usuario.last_name}'

# Modelo Práctica
class Practica(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('finalizada', 'Finalizada'),
    ]

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='practicas')
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='pendiente')
    fecha_inscripcion = models.DateField()

    def __str__(self):
        return f'Práctica {self.pk} - {self.get_estado_display()}'
    
# Modelo Ficha de Inscripción
class FichaInscripcion(models.Model):
    ESTADOS = [
            ('Pendiente', 'Pendiente'),
            ('Aprobada', 'Aprobada'),
            ('Rechazada', 'Rechazada'),
            ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='Pendiente')
    estudiante = models.ForeignKey('Estudiante', on_delete=models.CASCADE)
    practica = models.ForeignKey('Practica', on_delete=models.CASCADE, null=True, blank=True)  # Permite nulo
    practica1 = models.BooleanField(default=False)
    practica2 = models.BooleanField(default=False)
    razon_social = models.CharField(max_length=255)
    direccion_empresa = models.CharField(max_length=255)
    jefe_directo = models.CharField(max_length=255)
    cargo = models.CharField(max_length=100)
    telefono_jefe = models.CharField(max_length=20)
    correo_jefe = models.EmailField()
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()
    horario_trabajo = models.CharField(max_length=100)
    horario_colacion = models.CharField(max_length=100)
    cargo_desarrollar = models.CharField(max_length=100)
    depto_trabajar = models.CharField(max_length=100)
    actividades_realizar = models.CharField(max_length=100)

    def __str__(self):
        return f'Ficha Inscripción - {self.estudiante}'

# Modelo Autoevaluación
class Autoevaluacion(models.Model):
    practica = models.ForeignKey(Practica, on_delete=models.CASCADE)
    nota = models.DecimalField(max_digits=3, decimal_places=1)
    observaciones = models.TextField()

    def __str__(self):
        return f'Autoevaluación - Práctica {self.practica.pk}'

# Modelo Informe Confidencial
class InformeConfidencial(models.Model):
    practica = models.ForeignKey(Practica, on_delete=models.CASCADE)
    rubrica = models.ForeignKey('Rubrica', on_delete=models.CASCADE)
    comentario = models.TextField()

    def __str__(self):
        return f'Informe Confidencial - Práctica {self.practica.pk}'

# Modelo Rubrica
class Rubrica(models.Model):
    tipo_informe = models.CharField(max_length=100)
    criterio1 = models.CharField(max_length=100)
    criterio2 = models.CharField(max_length=100)
    ponderacion_criterio1 = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f'Rubrica: {self.tipo_informe}'

# Modelo Informe de Avances
class InformeAvances(models.Model):
    practica = models.ForeignKey(Practica, on_delete=models.CASCADE)
    rubrica = models.ForeignKey(Rubrica, on_delete=models.CASCADE)
    nota_avance = models.DecimalField(max_digits=3, decimal_places=1)
    retroalimentacion = models.TextField()
    archivo_informe_avances = models.FileField(upload_to='informes_avances/',null=True,blank=True)
    intentos_subida = models.PositiveIntegerField(default=0)

    # Máximo de intentos permitidos
    MAX_INTENTOS = 2

    def __str__(self):
        return f'Informe Avances - Práctica {self.practica.pk}'

# Modelo Informe Final
class InformeFinal(models.Model):
    practica = models.ForeignKey(Practica, on_delete=models.CASCADE)
    rubrica = models.ForeignKey(Rubrica, on_delete=models.CASCADE)
    nota = models.DecimalField(max_digits=3, decimal_places=1)
    retroalimentacion = models.TextField()
    archivo_informe_final = models.FileField(upload_to='informes_finales/', null=True, blank=True)
    intentos_subida_final = models.PositiveIntegerField(default=0)

    # Máximo de intentos permitidos
    MAX_INTENTOS = 2

    def __str__(self):
        return f'Informe Final - Práctica {self.practica.pk}'
    
class Document(models.Model):
    DOCUMENT_TYPES = [
        ('reglamento', 'Reglamento Práctica Profesional'),
        ('inscripcion', 'Ficha de inscripción práctica profesional'),
        ('avance', 'Informe de avances'),
        ('autoevaluacion', 'Autoevaluación'),
    ]
    
    tipo = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    archivo = models.FileField(upload_to='documentos_estaticos/')
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.get_tipo_display()
    

class PracticaConfig(models.Model):
    fecha_inicio_limite = models.DateField(default="2024-01-01")  # Fecha predeterminada
    fecha_termino_limite = models.DateField(default="2024-12-31")  # Fecha predeterminada

    def __str__(self):
        return f"Configuración Práctica: {self.fecha_inicio_limite} - {self.fecha_termino_limite}"

