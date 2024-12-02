from django.urls import path
from . import views

urlpatterns = [
    path('estudiante/', views.estudiante_view, name='estudiantes_main'),
    path('inscripcion_practica/', views.inscripcion_practica_view, name='inscripcion_practica'),
    path('detalle_practica/<int:solicitud_id>/', views.detalle_practica, name='detalle_practica'),
    path('ver_ficha/<int:solicitud_id>/', views.ver_ficha, name='ver_ficha'),
    path('autoevaluacion/<int:solicitud_id>/', views.autoevaluacion, name='autoevaluacion'),
    path('ver_autoevaluacion/<int:solicitud_id>/', views.ver_autoevaluacion, name='ver_autoevaluacion'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('descargar_plantilla/<int:practica_id>/', views.descargar_plantilla, name='descargar_plantilla'),
    path('descargar-final/<int:solicitud_id>/', views.descargar_archivo_final, name='descargar_archivo_final'),
]