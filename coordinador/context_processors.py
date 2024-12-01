from coordinador.models import FichaInscripcion


def fichas_pendientes(request):
    # Contamos las fichas de inscripción en estado pendiente
    pendientes = FichaInscripcion.objects.filter(estado='pendiente').count()
    return {'pendientes': pendientes}