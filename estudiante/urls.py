from django.urls import path
from . import views
from .views import verificar_practica1

urlpatterns = [
    path('estudiante/', views.estudiante_view, name='estudiantes_main'),
    path('inscripcion_practica/', views.inscripcion_practica_view, name='inscripcion_practica'),
    path('api/verificar_practica1/', verificar_practica1, name='verificar_practica1'),
]