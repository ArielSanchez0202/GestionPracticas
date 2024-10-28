# autenticacion/signals.py
from django.apps import apps
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate

def create_groups(sender, **kwargs):
    # Crear grupos si no existen
    Group.objects.get_or_create(name='Coordinador')
    Group.objects.get_or_create(name='Estudiante')

# Conectar la señal en el módulo de señales
post_migrate.connect(create_groups)
