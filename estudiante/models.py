from django.db import models

# Create your models here.
class InscripcionPractica(models.Model):
    ESTADOS = [
            ('Pendiente', 'Pendiente'),
            ('Aprobada', 'Aprobada'),
            ('Rechazada', 'Rechazada'),
            ]
    
    estado = models.CharField(max_length=10, choices=ESTADOS, default='Pendiente')
    nombre_completo = models.CharField(max_length=255)
    rut = models.CharField(max_length=12)  # Puedes ajustar el tamaño según sea necesario
    domicilio = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    carrera = models.CharField(max_length=100)
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
    horario_trabajo = models.CharField(max_length=100)  # Puedes ajustarlo según lo que necesitas
    horario_colacion = models.CharField(max_length=100)
    cargo_desarrollar = models.CharField(max_length=100)
    depto_trabajar = models.CharField(max_length=100)
    actividades_realizar = models.CharField(max_length=100)
    archivo_informe_avances = models.FileField(upload_to='informes_avances/',null=True,blank=True)
    intentos_subida = models.PositiveIntegerField(default=0)
    archivo_informe_final = models.FileField(upload_to='informes_finales/', null=True, blank=True)
    intentos_subida_final = models.PositiveIntegerField(default=0)

    # Máximo de intentos permitidos
    MAX_INTENTOS = 2
    class Meta:
        db_table = 'estudiante_inscripcionpractica'  # Enlazar a la tabla específica

    def __str__(self):
        return self.nombre_completo