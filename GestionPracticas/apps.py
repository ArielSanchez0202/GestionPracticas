from django.apps import AppConfig
from django_q.models import Schedule

class CoordinadorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coordinador'

    def ready(self):
        # Verifica si la tarea ya existe para evitar duplicados
        if not Schedule.objects.filter(func='coordinador.tasks.actualizar_estado_practicas').exists():
            Schedule.objects.create(
                func='coordinador.tasks.actualizar_estado_practicas',
                schedule_type=Schedule.DAILY,  # Corre diariamente
            )
