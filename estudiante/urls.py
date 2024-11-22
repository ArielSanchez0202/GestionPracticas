from django.urls import path
from . import views
from .views import verificar_practica1

urlpatterns = [
    path('estudiante/', views.estudiante_view, name='estudiantes_main'),
    path('inscripcion_practica/', views.inscripcion_practica_view, name='inscripcion_practica'),
    path('api/verificar_practica1/', verificar_practica1, name='verificar_practica1'),
    path('detalle_practica/<int:id>/', views.detalle_practica, name='detalle_practica'),
    path('ver_ficha/<int:id>/', views.ver_ficha, name='ver_ficha'),
    path('autoevaluacion/<int:id>/', views.autoevaluacion, name='autoevaluacion'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('descargar_plantilla/<int:id>/', views.descargar_plantilla, name='descargar_plantilla'),
    path('descargar-final/<int:id>/', views.descargar_archivo_final, name='descargar_archivo_final'),
]