# practicas/tasks.py
from datetime import date
from django.core.mail import send_mail
from django.conf import settings
from coordinador.models import Practica
from coordinador.views import enviar_formulario  # Importa la función enviar_formulario

def actualizar_estado_practicas():
    hoy = date.today()
    practicas_pendientes = Practica.objects.filter(estado__in=['en_progreso'], ficha__fecha_termino__lt=hoy)

    for practica in practicas_pendientes:
        if not practica.ficha:
            print(f'Práctica {practica.pk} no tiene ficha asociada. Saltando...')
            continue  # Si no tiene ficha, salta esta práctica
        
        practica.estado = 'finalizada'
        practica.save()
        print(f'Práctica {practica.pk} actualizada a "finalizada"')

        # Llamar a enviar_formulario
        enviar_formulario(None, practica.ficha.id)
