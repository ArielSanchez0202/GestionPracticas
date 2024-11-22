from django.db.models.signals import post_save
from django.dispatch import receiver
from coordinador.models import Practica, FichaInscripcion

@receiver(post_save, sender=FichaInscripcion)
def asociar_practica(sender, instance, **kwargs):
    if not instance.practica:  # Si no hay una práctica asociada
        # Crear una nueva práctica
        practica = Practica.objects.create(
            estudiante=instance.estudiante,
            estado='pendiente',
            fecha_inscripcion=instance.fecha_inicio,  # Usar fecha_inicio como fecha de inscripción
        )
        # Asociar la práctica creada a la ficha
        instance.practica = practica
