from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Practica, FichaInscripcion

@receiver(post_save, sender=FichaInscripcion)
def asociar_practica(sender, instance, created, **kwargs):
    if created and not instance.practica:  # Si la ficha es recién creada y no tiene una práctica
        # Crear una nueva práctica
        practica = Practica.objects.create(
            estudiante=instance.estudiante,
            estado='pendiente',
            fecha_inscripcion=instance.fecha_inicio,  # Usar fecha_inicio como fecha de inscripción
        )
        # Asociar la práctica creada a la ficha
        instance.practica = practica
        # Guardar la ficha con la práctica asociada
        instance.save()  # Guardar la ficha para persistir la relación
