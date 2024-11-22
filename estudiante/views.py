from django.shortcuts import render, redirect, get_object_or_404
from autenticacion.decorators import estudiante_required
from coordinador.models import Estudiante, Practica, FichaInscripcion, InformeAvances, InformeFinal, Document
from django.http import HttpResponse, JsonResponse, FileResponse
from .models import InscripcionPractica
from datetime import datetime
from django.conf import settings
import os
from coordinador.models import Document, PracticaConfig


# Create your views here.
@estudiante_required
def estudiante_view(request):
    # Obtener el estudiante asociado al usuario en sesión
    estudiante = Estudiante.objects.get(usuario=request.user)

    # Filtrar las prácticas de este estudiante (usando el modelo Practica)
    practicas = Practica.objects.filter(estudiante=estudiante)

    context = {
        'practicas': practicas,
    }
    return render(request, 'estudiante.html', context)

@estudiante_required
def inscripcion_practica_view(request):
    estudiante = Estudiante.objects.get(usuario=request.user)  # Obtener el estudiante logueado

    # Verificar si el estudiante ya tiene ambas prácticas (I y II)
    practica1_inscrita = FichaInscripcion.objects.filter(estudiante=estudiante, practica1=True).exists()
    practica2_inscrita = FichaInscripcion.objects.filter(estudiante=estudiante, practica2=True).exists()

    # Si ya tiene ambas prácticas, mostramos un mensaje y no permitimos más inscripciones
    if practica1_inscrita and practica2_inscrita:
        return render(request, 'inscripcion_practica.html', {
            'error': 'Ya tienes ambas prácticas (I y II) inscritas. No puedes agregar más.'
        })

    # Obtener límites de fecha configurados por el coordinador
    configuracion = PracticaConfig.objects.first()
    fecha_inicio_limite = configuracion.fecha_inicio_limite if configuracion else None
    fecha_termino_limite = configuracion.fecha_termino_limite if configuracion else None

    if request.method == 'POST':
        # Recuperar los datos enviados por el formulario
        practica1 = True if request.POST.get('practica1') else False  # checkbox
        practica2 = True if request.POST.get('practica2') else False  # checkbox
        razon_social = request.POST.get('razon_social')
        direccion_empresa = request.POST.get('direccion_empresa')
        jefe_directo = request.POST.get('jefe_directo')
        cargo = request.POST.get('cargo')
        telefono_jefe = request.POST.get('telefono_jefe')
        correo_jefe = request.POST.get('correo_jefe')

        # Convertir las fechas al formato correcto
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_termino = request.POST.get('fecha_termino')

        try:
            # Asegurarse de que las fechas estén en el formato YYYY-MM-DD
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_termino = datetime.strptime(fecha_termino, '%Y-%m-%d').date()

            # Validar fechas contra los límites
            if fecha_inicio_limite and fecha_inicio < fecha_inicio_limite:
                raise ValueError(f'La fecha de inicio no puede ser anterior a {fecha_inicio_limite}.')
            if fecha_termino_limite and fecha_termino > fecha_termino_limite:
                raise ValueError(f'La fecha de término no puede ser posterior a {fecha_termino_limite}.')

        except ValueError as e:
            # Manejar el error si las fechas no están en el formato correcto o no cumplen con los límites
            return render(request, 'inscripcion_practica.html', {
                'error': str(e),
                'estudiante': estudiante,
            })

        horario_trabajo = request.POST.get('horario_trabajo')
        horario_colacion = request.POST.get('horario_colacion')
        cargo_desarrollar = request.POST.get('cargo_desarrollar')
        depto_trabajar = request.POST.get('depto_trabajar')
        actividades_realizar = request.POST.get('actividades_realizar')

        # Crear una nueva instancia del modelo FichaInscripcion
        inscripcion = FichaInscripcion(
            estudiante=estudiante,  # Relacionar con el estudiante logueado
            practica1=practica1,
            practica2=practica2,
            razon_social=razon_social,
            direccion_empresa=direccion_empresa,
            jefe_directo=jefe_directo,
            cargo=cargo,
            telefono_jefe=telefono_jefe,
            correo_jefe=correo_jefe,
            fecha_inicio=fecha_inicio,
            fecha_termino=fecha_termino,
            horario_trabajo=horario_trabajo,
            horario_colacion=horario_colacion,
            cargo_desarrollar=cargo_desarrollar,
            depto_trabajar=depto_trabajar,
            actividades_realizar=actividades_realizar
        )

        # Guardar la inscripción en la base de datos
        try:
            inscripcion.save()
            return redirect('estudiantes_main')
        except Exception as e:
            print(f'Error al guardar: {e}')

    context = {
        'estudiante': estudiante,
        'fecha_inicio_limite': fecha_inicio_limite,
        'fecha_termino_limite': fecha_termino_limite,
    }
    return render(request, 'inscripcion_practica.html', context)

@estudiante_required
def verificar_practica1(request):
    estudiante = Estudiante.objects.get(usuario=request.user)  # Obtener el estudiante logueado
    existe_practica1 = FichaInscripcion.objects.filter(estudiante__rut=estudiante.rut, practica1=True).exists()
    existe_practica2 = FichaInscripcion.objects.filter(estudiante__rut=estudiante.rut, practica2=True).exists()
    return JsonResponse({'existe_practica1': existe_practica1, 'existe_practica2': existe_practica2})

@estudiante_required
def detalle_practica(request, id):
    practica = get_object_or_404(Practica, id=id)    
    documento = Document.objects.filter(tipo='inscripcion').first()

    if request.method == "POST":
        if "archivo_informe_avances" in request.FILES:
            archivo = request.FILES.get("archivo_informe_avances")
            if archivo:
                informe_avances = InformeAvances.objects.filter(practica=practica).first()
                if not informe_avances:
                    informe_avances = InformeAvances(practica=practica, intentos_subida=0)
                if informe_avances.archivo_informe_avances:
                    informe_avances.archivo_informe_avances.delete()  # Eliminar archivo anterior
                informe_avances.archivo_informe_avances = archivo
                informe_avances.intentos_subida += 1
                informe_avances.save()

        if "archivo_informe_final" in request.FILES:
            archivo_final = request.FILES.get("archivo_informe_final")
            if archivo_final:
                informe_final = InformeFinal.objects.filter(practica=practica).first()
                if not informe_final:
                    informe_final = InformeFinal(practica=practica, intentos_subida_final=0)
                if informe_final.archivo_informe_final:
                    informe_final.archivo_informe_final.delete()  # Eliminar archivo anterior
                informe_final.archivo_informe_final = archivo_final
                informe_final.intentos_subida_final += 1
                informe_final.save()

        return redirect('detalle_practica', id=practica.id)

    # Calcular intentos restantes desde los modelos relacionados
    informe_avances = InformeAvances.objects.filter(practica=practica).first()
    informe_final = InformeFinal.objects.filter(practica=practica).first()

    intentos_restantes_avances = max(informe_avances.MAX_INTENTOS - informe_avances.intentos_subida, 0) if informe_avances else 0
    intentos_restantes_final = max(informe_final.MAX_INTENTOS - informe_final.intentos_subida_final, 0) if informe_final else 0

    return render(request, 'detalle_practica.html', {
        'practica': practica,
        'documento': documento,
        'intentos_restantes_avances': intentos_restantes_avances,
        'intentos_restantes_final': intentos_restantes_final,
    })


@estudiante_required
def ver_ficha(request, solicitud_id,):
    # Obtener la solicitud de práctica específica por su ID
    solicitud = get_object_or_404(FichaInscripcion, pk=solicitud_id)
    # Renderizar el template y pasar la solicitud al contexto
    return render(request, 'ver_ficha.html', {'solicitud': solicitud})

@estudiante_required
def descargar_plantilla(request, practica_id):
    file_path = os.path.join(settings.BASE_DIR, 'estudiante', 'static', 'documents', 'Plantilla_informe.docx')

    # Verificar si el archivo existe
    if os.path.exists(file_path):
        # Enviar el archivo como respuesta HTTP para la descarga
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='Plantilla_informe.docx')
    else:
        # Si no se encuentra el archivo, enviar un error
        return HttpResponse('Archivo no encontrado', status=404)
    
@estudiante_required
def autoevaluacion(request, solicitud_id):
    # Obtener el estudiante actual
    estudiante = get_object_or_404(Estudiante, usuario=request.user)
    
    # Obtener la solicitud de práctica
    solicitud = get_object_or_404(FichaInscripcion, id=solicitud_id)
    
    context = {
        'estudiante': estudiante,
        'solicitud': solicitud,
        'solicitud_id': solicitud_id,  # Agregar solicitud_id al contexto
    }
    return render(request, 'autoevaluacion.html', context)

@estudiante_required
def dashboard(request):
    estudiante = Estudiante.objects.get(usuario=request.user)
    # Filtrar las solicitudes solo del estudiante actual
    total_solicitudes = FichaInscripcion.objects.filter(estudiante__rut=estudiante.rut).count()
    solicitudes_pendientes = FichaInscripcion.objects.filter(estudiante__rut=estudiante.rut, estado='Pendiente').count()
    solicitudes_aprobadas = FichaInscripcion.objects.filter(estudiante__rut=estudiante.rut, estado='Aprobada').count()
    solicitudes_rechazadas = FichaInscripcion.objects.filter(estudiante__rut=estudiante.rut, estado='Rechazada').count()
    solicitudes_recientes = FichaInscripcion.objects.filter(estudiante__rut=estudiante.rut).order_by('-id')[:5]

    context = {
        'total_solicitudes': total_solicitudes,
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_aprobadas': solicitudes_aprobadas,
        'solicitudes_rechazadas': solicitudes_rechazadas,
        'solicitudes_recientes': solicitudes_recientes,
    }
    return render(request, 'dashboard.html', context)

@estudiante_required
def descargar_archivo_final(request, practica_id):
    # Buscar la inscripción de práctica usando el ID
    practica = get_object_or_404(FichaInscripcion, id=practica_id)
    
    # Verificar que el número de intentos esté agotado
    if practica.intentos_subida_final < 2:
        # Verificar si hay un archivo subido
        if practica.archivo_informe_final:
            archivo_path = practica.archivo_informe_final.path  # Obtener la ruta del archivo
            return FileResponse(open(archivo_path, 'rb'), as_attachment=True, filename=practica.archivo_informe_final.name)
        else:
            return HttpResponse("No se ha subido ningún archivo para este informe final.", status=404)
    else:
        return HttpResponse("No se puede descargar el informe final, los intentos no han sido agotados.", status=403)