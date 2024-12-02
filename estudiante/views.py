from django.shortcuts import render, redirect, get_object_or_404
from autenticacion.decorators import estudiante_required
from coordinador.models import Estudiante, Practica, FichaInscripcion, InformeAvances, InformeFinal, Document, Autoevaluacion
from django.http import HttpResponse, JsonResponse, FileResponse
from datetime import datetime, date
from django.conf import settings
import os
from coordinador.models import Document, PracticaConfig


# Create your views here.
@estudiante_required
def estudiante_view(request):
    # Obtener el estudiante asociado al usuario en sesión
    estudiante = get_object_or_404(Estudiante, usuario=request.user)

    # Filtrar las fichas de inscripción asociadas al estudiante
    fichas_inscripcion = FichaInscripcion.objects.filter(estudiante=estudiante)

    # Verificar y actualizar el estado de las prácticas si la fecha de término coincide con la fecha actual
    for ficha in fichas_inscripcion:
        if ficha.fecha_termino <= date.today():
            # Si la fecha de término es hoy o anterior, actualizamos el estado de la práctica
            if ficha.practica:
                ficha.practica.estado = 'finalizada'
                ficha.practica.save()

    context = {
        'fichas_inscripcion': fichas_inscripcion,
    }

    return render(request, 'estudiante.html', context)

@estudiante_required
def inscripcion_practica_view(request):
    estudiante = Estudiante.objects.get(usuario=request.user)  # Obtener el estudiante logueado

    # Verificar si el estudiante ya tiene ambas prácticas inscritas (sin contar rechazadas)
    practica1_inscrita = FichaInscripcion.objects.filter(
        estudiante=estudiante, practica1=True
    ).exclude(estado='Rechazada').exists()
    practica2_inscrita = FichaInscripcion.objects.filter(
        estudiante=estudiante, practica2=True
    ).exclude(estado='Rechazada').exists()

    # Verificar si la práctica 1 está aprobada
    practica1_aprobada = FichaInscripcion.objects.filter(
        estudiante=estudiante, practica1=True, estado='Aprobada'
    ).exists()

    # Verificar si la práctica 1 está aprobada
    practica2_aprobada = FichaInscripcion.objects.filter(
        estudiante=estudiante, practica2=True, estado='Aprobada'
    ).exists()

    # Obtener fichas con estado "Pendiente" o "Jefe Carrera" para prácticas 1 y 2
    practica1_pendiente_o_jefe_carrera = FichaInscripcion.objects.filter(
        estudiante=estudiante, practica1=True, estado__in=['Pendiente', 'Jefe Carrera']
    ).exists()
    practica2_pendiente_o_jefe_carrera = FichaInscripcion.objects.filter(
        estudiante=estudiante, practica2=True, estado__in=['Pendiente', 'Jefe Carrera']
    ).exists()

    # Si ya tiene ambas prácticas inscritas (sin contar rechazadas), mostramos un mensaje
    if practica1_aprobada and practica2_aprobada:
        return render(request, 'inscripcion_practica.html', {
            'error': 'Ya tienes ambas prácticas (I y II) inscritas y aprobadas. No puedes agregar más.'
        })

    # Obtener límites de fecha configurados por el coordinador
    configuracion = PracticaConfig.objects.first()
    fecha_inicio_limite = configuracion.fecha_inicio_limite if configuracion else None
    fecha_termino_limite = configuracion.fecha_termino_limite if configuracion else None

    if request.method == 'POST':
        # Recuperar el tipo de práctica seleccionado
        tipo_practica = request.POST.get('tipo_practica')
        practica1 = tipo_practica == '1'
        practica2 = tipo_practica == '2'

        # Validar si el estudiante puede inscribir la práctica 2
        if practica2:
            if not practica1_aprobada:
                return render(request, 'inscripcion_practica.html', {
                    'error': 'No puedes inscribir la Práctica II hasta que la Práctica I esté aprobada.',
                    'estudiante': estudiante,
                })

        # Mostrar mensaje si intenta inscribir práctica 1 ya aprobada
        if practica1 and practica1_aprobada:
            return render(request, 'inscripcion_practica.html', {
                'error': 'Ya tienes inscrita y aprobada la Práctica I.',
                'estudiante': estudiante,
            })

        # Validar si la práctica seleccionada está en estado "Pendiente" o "Jefe Carrera"
        if practica1 and practica1_pendiente_o_jefe_carrera:
            return render(request, 'inscripcion_practica.html', {
                'error': 'No puedes inscribir nuevamente en la Práctica I mientras esté en estado "Pendiente".',
                'estudiante': estudiante,
            })
        if practica2 and practica2_pendiente_o_jefe_carrera:
            return render(request, 'inscripcion_practica.html', {
                'error': 'No puedes inscribirte nuevamente en la Práctica II mientras esté en estado "Pendiente".',
                'estudiante': estudiante,
            })

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
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_termino = datetime.strptime(fecha_termino, '%Y-%m-%d').date()

            # Validar fechas contra los límites
            if fecha_inicio_limite and fecha_inicio < fecha_inicio_limite:
                raise ValueError(f'La fecha de inicio no puede ser anterior a {fecha_inicio_limite}.')
            if fecha_termino_limite and fecha_termino > fecha_termino_limite:
                raise ValueError(f'La fecha de término no puede ser posterior a {fecha_termino_limite}.')

        except ValueError as e:
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
            estudiante=estudiante,
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

        try:
            inscripcion.save()
            return redirect('estudiantes_main')
        except Exception as e:
            print(f'Error al guardar: {e}')

    context = {
        'estudiante': estudiante,
        'fecha_inicio_limite': fecha_inicio_limite,
        'fecha_termino_limite': fecha_termino_limite,
        'practica1_aprobada': practica1_aprobada,
    }

    return render(request, 'inscripcion_practica.html', context)

@estudiante_required
def detalle_practica(request, solicitud_id):
    practica = get_object_or_404(Practica, id=solicitud_id)
    ficha_inscripcion = FichaInscripcion.objects.filter(practica=practica).first()    
    autoevaluacion = Autoevaluacion.objects.filter(practica=practica).first()
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

        return redirect('detalle_practica', solicitud_id=practica.id)

    # Calcular intentos restantes desde los modelos relacionados
    informe_avances = InformeAvances.objects.filter(practica=practica).first()
    informe_final = InformeFinal.objects.filter(practica=practica).first()

    # Obtener nombres de los archivos subidos
    archivo_informe_avances = informe_avances.archivo_informe_avances.name if informe_avances and informe_avances.archivo_informe_avances else None
    archivo_informe_final = informe_final.archivo_informe_final.name if informe_final and informe_final.archivo_informe_final else None

    # Verificar si hay un informe de avances asociado
    informe_avances_enviado = InformeAvances.objects.filter(practica=practica).exists()
    
    # Nota de la autoevaluación (si existe)
    nota_autoevaluacion = autoevaluacion.nota if autoevaluacion else None
    # Verificar si hay una autoevaluación asociada
    autoevaluacion_completada = Autoevaluacion.objects.filter(practica=practica).exists()

    intentos_restantes_avances = max(informe_avances.MAX_INTENTOS - informe_avances.intentos_subida, 0) if informe_avances else 2
    intentos_restantes_final = max(informe_final.MAX_INTENTOS - informe_final.intentos_subida_final, 0) if informe_final else 2

    return render(request, 'detalle_practica.html', {
        'practica': practica,
        'ficha_inscripcion': ficha_inscripcion,
        'estado_ficha': ficha_inscripcion.estado,
        'documento': documento,
        'intentos_restantes_avances': intentos_restantes_avances,
        'intentos_restantes_final': intentos_restantes_final,
        'archivo_informe_avances': archivo_informe_avances,
        'archivo_informe_final': archivo_informe_final,
        'nota_autoevaluacion': nota_autoevaluacion,
        'autoevaluacion_completada': autoevaluacion_completada,
        'informe_avances_enviado': informe_avances_enviado,
    })


@estudiante_required
def ver_ficha(request, solicitud_id,):
    # Obtener la práctica específica
    practica = get_object_or_404(Practica, id=solicitud_id)
    # Obtener el estudiante actual
    estudiante = get_object_or_404(Estudiante, usuario=request.user)   
    # Obtener la solicitud de práctica
    solicitud = get_object_or_404(FichaInscripcion, id=solicitud_id)
    
    # Contexto para pasar a la plantilla
    context = {
        'practica': practica,
        'estudiante': estudiante,
        'solicitud': solicitud,
    }
    
    # Renderizar la plantilla con el contexto
    return render(request, 'ver_ficha.html', context)

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
    # Obtener la práctica y estudiante asociados
    practica = get_object_or_404(Practica, id=solicitud_id)
    estudiante = get_object_or_404(Estudiante, usuario=request.user)
    solicitud = get_object_or_404(FichaInscripcion, id=solicitud_id)

    if request.method == 'POST':
        # Define los puntajes por respuesta
        puntajes = {'Siempre': 4, 'Frecuentemente': 3, 'A veces': 2, 'Nunca': 1}
        total_preguntas = 11  # Número total de preguntas
        puntaje_maximo = total_preguntas * 4

        # Obtener y procesar las respuestas del formulario
        puntaje_obtenido = sum(
            puntajes.get(request.POST.get(f'pregunta{i}', 'Nunca'), 0)
            for i in range(1, total_preguntas + 1)
        )

        # Calcular la nota (escala de 1.0 a 7.0)
        nota = 1.0 + (puntaje_obtenido / puntaje_maximo) * 6.0

        # Obtener otros campos del formulario
        observaciones = request.POST.get('observaciones', '')
        comentarios1 = request.POST.get('comentarios1', '')
        comentarios2 = request.POST.get('comentarios2', '')
        comentarios3 = request.POST.get('comentarios3', '')
        pregunta12 = request.POST.get('pregunta12', '')

        # Crear y guardar la autoevaluación
        autoevaluacion = Autoevaluacion.objects.create(
            practica=practica,
            nota=round(nota, 2),
            observaciones=observaciones,
            pregunta1=request.POST.get('pregunta1', ''),
            pregunta2=request.POST.get('pregunta2', ''),
            pregunta3=request.POST.get('pregunta3', ''),
            pregunta4=request.POST.get('pregunta4', ''),
            pregunta5=request.POST.get('pregunta5', ''),
            pregunta6=request.POST.get('pregunta6', ''),
            pregunta7=request.POST.get('pregunta7', ''),
            pregunta8=request.POST.get('pregunta8', ''),
            pregunta9=request.POST.get('pregunta9', ''),
            pregunta10=request.POST.get('pregunta10', ''),
            pregunta11=request.POST.get('pregunta11', ''),
            comentarios1=comentarios1,
            comentarios2=comentarios2,
            pregunta12=pregunta12,
            comentarios3=comentarios3
        )

        # Redirigir al usuario a una página de éxito o detalle
        return redirect('detalle_practica', solicitud_id=solicitud_id) 

    # Si no es un POST, renderiza el formulario vacío
    return render(request, 'autoevaluacion.html', {
        'practica': practica,
        'estudiante': estudiante,
        'solicitud': solicitud,
        'solicitud_id': solicitud_id,
    })

@estudiante_required
def ver_autoevaluacion(request, solicitud_id):
    # Obtener la práctica específica
    practica = get_object_or_404(Practica, id=solicitud_id)
    # Obtener el estudiante actual
    estudiante = get_object_or_404(Estudiante, usuario=request.user)
    # Obtener la solicitud de práctica
    solicitud = get_object_or_404(FichaInscripcion, id=solicitud_id)
    # Obtener la autoevaluación asociada a la práctica
    autoevaluacion = Autoevaluacion.objects.filter(practica=practica).first()

    # Contexto para pasar a la plantilla
    context = {
        'practica': practica,
        'estudiante': estudiante,
        'solicitud': solicitud,
        'autoevaluacion': autoevaluacion,
    }

    return render(request, 'ver_autoevaluacion.html', context)

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