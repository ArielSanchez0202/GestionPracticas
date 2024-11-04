from django.core.exceptions import PermissionDenied
############DECORADORES PARA RESTRINIGIR ACCESO A LAS VISTAS######################
def coordinador_required(view_func):
    """
    Decorador para permitir acceso solo a usuarios en el grupo 'Coordinador'.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.groups.filter(name='Coordinador').exists():
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return _wrapped_view

def estudiante_required(view_func):
    """
    Decorador para permitir acceso solo a usuarios en el grupo 'Estudiante'.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.groups.filter(name='Estudiante').exists():
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return _wrapped_view