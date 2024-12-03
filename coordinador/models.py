from django.db import models
from django.contrib.auth.models import User  # Importa el modelo de usuario de Django
from datetime import datetime, date
import uuid
from django.utils.crypto import get_random_string

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
        ('rechazada', 'Rechazada'),
        ('finalizada', 'Finalizada'),
    ]

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='practicas')
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='pendiente')
    fecha_inscripcion = models.DateField(default=date.today)

    def __str__(self):
        return f'Práctica {self.pk} - {self.get_estado_display()}'
    
# Modelo Ficha de Inscripción
class FichaInscripcion(models.Model):
    ESTADOS = [
            ('Pendiente', 'Pendiente'),
            ('Aprobada', 'Aprobada'),
            ('Rechazada', 'Rechazada'),
            ('Jefe Carrera', 'Jefe Carrera'),
            ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    token = models.UUIDField(default=uuid.uuid4, null=True, blank=True)
    comentario = models.TextField(null=True, blank=True)
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
    nota = models.DecimalField(max_digits=3, decimal_places=1, null=True)
    observaciones = models.TextField(null=True)
    pregunta1 = models.CharField(max_length=20, choices=[('Siempre', 'Siempre'), 
                                                         ('Frecuentemente', 'Frecuentemente'),
                                                         ('A veces', 'A veces'),
                                                         ('Nunca', 'Nunca')])
    pregunta2 = models.CharField(max_length=20, choices=[('Siempre', 'Siempre'), 
                                                         ('Frecuentemente', 'Frecuentemente'),
                                                         ('A veces', 'A veces'),
                                                         ('Nunca', 'Nunca')])
    pregunta3 = models.CharField(max_length=20, choices=[('Siempre', 'Siempre'), 
                                                         ('Frecuentemente', 'Frecuentemente'),
                                                         ('A veces', 'A veces'),
                                                         ('Nunca', 'Nunca')])
    pregunta4 = models.CharField(max_length=20, choices=[('Siempre', 'Siempre'), 
                                                         ('Frecuentemente', 'Frecuentemente'),
                                                         ('A veces', 'A veces'),
                                                         ('Nunca', 'Nunca')])
    pregunta5 = models.CharField(max_length=20, choices=[('Siempre', 'Siempre'), 
                                                         ('Frecuentemente', 'Frecuentemente'),
                                                         ('A veces', 'A veces'),
                                                         ('Nunca', 'Nunca')])
    pregunta6 = models.CharField(max_length=20, choices=[('Siempre', 'Siempre'), 
                                                         ('Frecuentemente', 'Frecuentemente'),
                                                         ('A veces', 'A veces'),
                                                         ('Nunca', 'Nunca')])
    pregunta7 = models.CharField(max_length=20, choices=[('Siempre', 'Siempre'), 
                                                         ('Frecuentemente', 'Frecuentemente'),
                                                         ('A veces', 'A veces'),
                                                         ('Nunca', 'Nunca')])
    pregunta8 = models.CharField(max_length=20, choices=[('Siempre', 'Siempre'), 
                                                         ('Frecuentemente', 'Frecuentemente'),
                                                         ('A veces', 'A veces'),
                                                         ('Nunca', 'Nunca')])
    pregunta9 = models.CharField(max_length=20, choices=[('Siempre', 'Siempre'), 
                                                         ('Frecuentemente', 'Frecuentemente'),
                                                         ('A veces', 'A veces'),
                                                         ('Nunca', 'Nunca')])
    pregunta10 = models.CharField(max_length=20, choices=[('Siempre', 'Siempre'), 
                                                          ('Frecuentemente', 'Frecuentemente'),
                                                          ('A veces', 'A veces'),
                                                          ('Nunca', 'Nunca')])
    pregunta11 = models.CharField(max_length=20, choices=[('Siempre', 'Siempre'), 
                                                          ('Frecuentemente', 'Frecuentemente'),
                                                          ('A veces', 'A veces'),
                                                          ('Nunca', 'Nunca')])
    comentarios1 = models.TextField()
    comentarios2 = models.TextField(blank=True, null=True)
    pregunta12 = models.CharField(max_length=3, choices=[('Si', 'Sí'), ('No', 'No')])
    comentarios3 = models.TextField()


    def __str__(self):
        return f'Autoevaluación - Práctica {self.practica.pk}'
    
    class Meta:
        verbose_name = 'Autoevaluación'
        verbose_name_plural = 'Autoevaluaciones'

# Modelo Informe Confidencial
class InformeConfidencial(models.Model):
    ficha_inscripcion = models.OneToOneField(FichaInscripcion, on_delete=models.CASCADE, related_name='informe_confidencial')
    nota = models.FloatField(default=0)  # Cambié esto a FloatField
    practica = models.ForeignKey('Practica', on_delete=models.CASCADE, null=True, blank=True)  # Permite nulo

    # Aspectos técnicos
    calidad_trabajo = models.CharField(max_length=50, choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')])
    calidad_observacion = models.TextField(blank=True, null=True)

    efectividad_trabajo = models.CharField(max_length=50, choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')])
    efectividad_observacion = models.TextField(blank=True, null=True)

    conocimientos_profesionales = models.CharField(max_length=50, choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')])
    conocimientos_observacion = models.TextField(blank=True, null=True)

    adaptabilidad_cambios = models.CharField(max_length=50, choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')])
    adaptabilidad_observacion = models.TextField(blank=True, null=True)

    organizacion_trabajo = models.CharField(max_length=50, choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')])
    organizacion_observacion = models.TextField(blank=True, null=True)

    # Aspectos personales
    interes_trabajo = models.CharField(max_length=50, choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')])
    interes_observacion = models.TextField(blank=True, null=True)

    responsabilidad = models.CharField(max_length=50, choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')])
    responsabilidad_observacion = models.TextField(blank=True, null=True)

    cooperacion_trabajo = models.CharField(max_length=50, choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')])
    cooperacion_observacion = models.TextField(blank=True, null=True)

    creatividad = models.CharField(max_length=50, choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')])
    creatividad_observacion = models.TextField(blank=True, null=True)

    iniciativa = models.CharField(max_length=50, choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')])
    iniciativa_observacion = models.TextField(blank=True, null=True)

    integracion_grupo = models.CharField(max_length=50, choices=[('S', 'Siempre'), ('F', 'Frecuentemente'), ('A', 'A veces'), ('N', 'Nunca')])
    integracion_observacion = models.TextField(blank=True, null=True)

    # Preguntas adicionales
    positivo_recibir = models.BooleanField()
    tipo_especialidad = models.TextField(blank=True, null=True)

    # Información adicional
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def calcular_nota(self):
        # Definir los valores para cada respuesta
        valores = {
            'S': 7,
            'F': 5,
            'A': 3,
            'N': 1
        }

        # Lista de campos con las respuestas
        campos_respuesta = [
            self.calidad_trabajo,
            self.efectividad_trabajo,
            self.conocimientos_profesionales,
            self.adaptabilidad_cambios,
            self.organizacion_trabajo,
            self.interes_trabajo,
            self.responsabilidad,
            self.cooperacion_trabajo,
            self.creatividad,
            self.iniciativa,
            self.integracion_grupo
        ]

        # Sumar las notas de todos los campos
        total = sum(valores[respuesta] for respuesta in campos_respuesta if respuesta in valores)
        
        # Promediar y asignar la nota final
        self.nota = total / len(campos_respuesta)
        self.nota = round(self.nota, 1)

# Modelo Rubrica
class Rubrica(models.Model):
    tipo_informe = models.CharField(max_length=100)
    # Sección I: Contenido del Documento
    portada = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    introduccion = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    objetivo_general = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    objetivos_especificos = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    caracterizacion_empresa = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    datos_supervisor = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    desarrollo_practica = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    recomendaciones = models.CharField(
        max_length=50,
        choices=[
            ("Desempeño de excelencia", "Desempeño de excelencia"),
            ("Desempeño efectivo", "Desempeño efectivo"),
            ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
            ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
        ],
        blank=True,
        null=True
    )
    conclusiones = models.CharField(
        max_length=50,
        choices=[
            ("Desempeño de excelencia", "Desempeño de excelencia"),
            ("Desempeño efectivo", "Desempeño efectivo"),
            ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
            ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
        ],
        blank=True,
        null=True
    )
    anexos = models.CharField(
        max_length=50,
        choices=[
            ("Desempeño de excelencia", "Desempeño de excelencia"),
            ("Desempeño efectivo", "Desempeño efectivo"),
            ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
            ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
        ],
        blank=True,
        null=True
    )

    # Sección II: Formato
    formato_establecido = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    tercera_persona = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    cita_fuente = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    extension = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    tabla_grafico = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    ortografia = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    cohesion_coherencia = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    ideas_profundizacion = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    roles_impacto = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])
    riqueza_linguistica = models.CharField(max_length=50, choices=[
        ("Desempeño de excelencia", "Desempeño de excelencia"),
        ("Desempeño efectivo", "Desempeño efectivo"),
        ("Desempeño que se debe mejorar", "Desempeño que se debe mejorar"),
        ("Desempeño insatisfactorio", "Desempeño insatisfactorio"),
    ])

    # Comentarios
    comentarios = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Rubrica: {self.tipo_informe}'

# Modelo Informe de Avances
class InformeAvances(models.Model):
    practica = models.ForeignKey(Practica, on_delete=models.CASCADE)
    rubrica = models.ForeignKey(Rubrica, on_delete=models.CASCADE, null=True,blank=True)
    nota_avance = models.DecimalField(max_digits=3, decimal_places=1, null=True,blank=True)
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
    rubrica = models.ForeignKey(Rubrica, on_delete=models.CASCADE, null=True, blank=True)
    nota = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
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
    correo_director = models.EmailField(max_length=254, default="director@example.com")  # Correo predeterminado

    def __str__(self):
        return f"Configuración Práctica: {self.fecha_inicio_limite} - {self.fecha_termino_limite}"


from django.utils.crypto import get_random_string

def generar_token():
    return get_random_string(32)

class FormularioToken(models.Model):
    ficha_inscripcion = models.OneToOneField('FichaInscripcion', on_delete=models.CASCADE, related_name='formulario_token')
    token = models.CharField(max_length=64, unique=True, default=generar_token)  # Usar la función generar_token
    enviado = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token para {self.ficha_inscripcion.estudiante}"


############################################################

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('info', 'Información'),
        ('alerta', 'Alerta'),
        ('exito', 'Éxito'),
        ('error', 'Error'),
    ]
    mensaje = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='info')
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.usuario.username}: {self.mensaje[:20]}"