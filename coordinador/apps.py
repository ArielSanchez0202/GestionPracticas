from django.apps import AppConfig


class CoordinadorConfig(AppConfig):
    name = 'coordinador'

    def ready(self):
        import coordinador.signals
