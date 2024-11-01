# coordinador/urls.py

from django.urls import path
from . import views
app_name = 'coordinador'

urlpatterns = [
    # Agrega aquí tus patrones de URL
    path('agregar_estudiante/', views.agregar_estudiante, name='agregar_estudiante'),
    path('carga_masiva/', views.carga_masiva_estudiantes, name='carga_masiva_estudiantes'),
    path('descargar_plantilla/', views.descargar_plantilla_estudiantes, name='descargar_plantilla_estudiantes'),
    path('listar_estudiantes/', views.listar_estudiantes, name='listar_estudiantes'),
    path('previsualizar_estudiantes/', views.previsualizar_estudiantes, name='previsualizar_estudiantes'),
    path('editar_estudiante/<int:estudiante_id>/', views.editar_estudiante, name='editar_estudiante'),
    path('detalle_estudiante/<int:estudiante_id>/', views.detalle_estudiante, name='detalle_estudiante'),
    #Lista Coordinadores
    path('listar_coordinador/',views.listar_coordinador,name='listar_coordinador')
]
