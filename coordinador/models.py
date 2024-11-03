from django.db import models
from django.contrib.auth.models import User  # Importa el modelo de usuario de Django
import uuid

# Modelo Coordinador
class Coordinador(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100, blank=True)
    correo = models.CharField(max_length=100 ,blank=True)
    rut = models.CharField(max_length=20, blank=True, unique=True)
    domicilio = models.CharField(max_length=255, blank=True)
    carrera = models.CharField(max_length=100, blank=True)
    numero = models.CharField(max_length=20, blank=True)

    def __str__(self):
        texto = "{0} ({1})"
        return texto.format(self.nombre, self.apellido)
# Modelo Estudiante
class Estudiante(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    rut = models.CharField(max_length=20, unique=True)
    domicilio = models.CharField(max_length=255)
    carrera = models.CharField(max_length=100)
    numero_telefono = models.CharField(max_length=20)  # Campo agregado para el número de teléfono

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
    practica = models.ForeignKey(Practica, on_delete=models.CASCADE)
    empresa = models.CharField(max_length=255)
    supervisor = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    def __str__(self):
        return f'Ficha Inscripción - Práctica {self.practica.pk}'

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

    def __str__(self):
        return f'Informe Avances - Práctica {self.practica.pk}'

# Modelo Informe Final
class InformeFinal(models.Model):
    practica = models.ForeignKey(Practica, on_delete=models.CASCADE)
    rubrica = models.ForeignKey(Rubrica, on_delete=models.CASCADE)
    nota = models.DecimalField(max_digits=3, decimal_places=1)
    retroalimentacion = models.TextField()

    def __str__(self):
        return f'Informe Final - Práctica {self.practica.pk}'
