from django.urls import path
from . import views
from .views import verificar_practica1

urlpatterns = [
    path('estudiante/', views.estudiante_view, name='estudiantes_main'),
    path('inscripcion_practica/', views.inscripcion_practica_view, name='inscripcion_practica'),
    path('api/verificar_practica1/', verificar_practica1, name='verificar_practica1'),
    path('listar_practicas/', views.listar_practicas, name='listar_practicas'),
    path('ver_formulario/<int:solicitud_id>/', views.ver_formulario, name='ver_formulario'),
    path('actualizar_estado/<int:solicitud_id>/', views.actualizar_estado, name='actualizar_estado'),
]