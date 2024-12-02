# coordinador/urls.py

from django.urls import path
from . import views
from .views import descargar_informe
urlpatterns = [
    # Agrega aquí tus patrones de URL
    path('agregar_estudiante/', views.agregar_estudiante, name='agregar_estudiante'),
    path('carga_masiva/', views.carga_masiva_estudiantes, name='carga_masiva_estudiantes'),
    path('descargar_plantilla/', views.descargar_plantilla_estudiantes, name='descargar_plantilla_estudiantes'),
    path('listar_estudiantes/', views.listar_estudiantes, name='listar_estudiantes'),
    path('previsualizar_estudiantes/', views.previsualizar_estudiantes, name='previsualizar_estudiantes'),
    path('editar_estudiante/<int:estudiante_id>/', views.editar_estudiante, name='editar_estudiante'),
    path('detalle_estudiante/<int:estudiante_id>/', views.detalle_estudiante, name='detalle_estudiante'),
    path('coordinadores/',views.coordinadores, name='coordinadores'),
    path('informes_avances/', views.informes_avances, name='informes_avances'),
    path('autoevaluaciones/', views.autoevaluaciones, name='autoevaluaciones'),
    path('actualizar-nota/', views.actualizar_nota, name='actualizar_nota'),
    path('actualizar-nota-informe-confidencial/', views.actualizar_nota_informe_confidencial, name='actualizar_nota_informe_confidencial'),
    path('revisar_autoevaluacion/<int:practica_id>/', views.revisar_autoevaluacion, name='revisar_autoevaluacion'),
    path('informes_finales/', views.informes_finales, name='informes_finales'),
    path('documentos/', views.documentos, name='documentos'),
    path('ver_documento/<int:document_id>/', views.ver_documento, name='ver_documento'),
    path('descargar_informe/<int:practica_id>/', descargar_informe, name='descargar_informe'),
    #Lista Coordinadores
    path('listar_coordinador/',views.listar_coordinador,name='listar_coordinador'),
    path('crear_coordinador/',views.crear_coordinador,name='crear_coordinador'),
    path('registrar_coordinador/',views.registrar_coordinador,name='registrar_coordinador'),
    path('editar_coordinador/<int:coordinador_id>',views.editar_coordinador,name='editar_coordinador'),
    #path('editarcoordinador/',views.editarcoordinador,name='editarcoordinador'),
    path('ver_coordinador/<int:coordinador_id>',views.ver_coordinador,name='ver_coordinador'),
    path('dashboard/', views.dashboard, name='dashboard_coordinador'),
    #asd
    path('listar_practicas/', views.listar_practicas, name='listar_practicas'),
    path('ver_formulario/<int:solicitud_id>/', views.ver_formulario, name='ver_formulario'),
    path('actualizar_estado/<int:solicitud_id>/', views.actualizar_estado, name='actualizar_estado'),
    path('configurar_fechas/', views.configurar_fechas, name='configurar_fechas'),
    path('generar-pdf-practica/<int:ficha_id>/', views.generar_pdf_practica, name='generar_pdf_practica'),
    ############INFORMES CONFIDENCIALES###############################
    path('enviar-formulario/<int:ficha_id>/', views.enviar_formulario, name='enviar_formulario'),
    path('formulario/<str:token>/', views.completar_formulario, name='completar_formulario'),
    path('listado_informes_confidenciales/', views.listado_informes_confidenciales, name='listado_informes_confidenciales'),
    path('editar_informe_confidencial/<int:informe_id>/', views.editar_informe_confidencial, name='editar_informe_confidencial'),
    ####################################################################
    path('detalle_practica_coordinador/<int:practica_id>/', views.detalle_practica_coordinador, name='detalle_practica_coordinador'),
]
