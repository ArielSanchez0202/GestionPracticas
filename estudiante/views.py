from django.shortcuts import render, redirect, get_object_or_404
from autenticacion.decorators import estudiante_required,coordinador_required
from coordinador.models import Estudiante, Practica , Coordinador
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from .models import InscripcionPractica
from datetime import datetime

# Create your views here.
@estudiante_required
def estudiante_view(request):
    # Obtener el estudiante asociado al usuario en sesión
    estudiante = Estudiante.objects.get(usuario=request.user)

    # Filtrar las prácticas de este estudiante
    practicas = InscripcionPractica.objects.filter(rut=estudiante.rut)

    context = {
        'practicas': practicas,
    }
    return render(request, 'estudiante.html', context)

@estudiante_required
def inscripcion_practica_view(request):
    estudiante = Estudiante.objects.get(usuario=request.user)  # Obtener el estudiante logueado

    # Verificar si el estudiante ya tiene ambas prácticas (I y II)
    practica1_inscrita = InscripcionPractica.objects.filter(rut=estudiante.rut, practica1=True).exists()
    practica2_inscrita = InscripcionPractica.objects.filter(rut=estudiante.rut, practica2=True).exists()

    # Si ya tiene ambas prácticas, mostramos un mensaje y no permitimos más inscripciones
    if practica1_inscrita and practica2_inscrita:
        return render(request, 'inscripcion_practica.html', {
            'error': 'Ya tienes ambas prácticas (I y II) inscritas. No puedes agregar más.'
        })

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
        except ValueError:
            # Manejar el error si las fechas no están en el formato correcto
            return render(request, 'inscripcion_practica.html', {
                'error': 'Formato de fecha inválido. Use YYYY-MM-DD.'
            })

        horario_trabajo = request.POST.get('horario_trabajo')
        horario_colacion = request.POST.get('horario_colacion')
        cargo_desarrollar = request.POST.get('cargo_desarrollar')
        depto_trabajar = request.POST.get('depto_trabajar')
        actividades_realizar = request.POST.get('actividades_realizar')

        # Crear una nueva instancia del modelo InscripcionPractica
        inscripcion = InscripcionPractica(
            nombre_completo=estudiante.usuario.get_full_name(),
            rut=estudiante.rut,
            domicilio=estudiante.domicilio,
            telefono=estudiante.numero_telefono,
            correo=estudiante.usuario.email,
            carrera=estudiante.carrera,
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
    }
    return render(request, 'inscripcion_practica.html', context)

@estudiante_required
def verificar_practica1(request):
    estudiante = Estudiante.objects.get(usuario=request.user)  # Obtener el estudiante logueado
    existe_practica1 = InscripcionPractica.objects.filter(rut=estudiante.rut, practica1=True).exists()
    existe_practica2 = InscripcionPractica.objects.filter(rut=estudiante.rut, practica2=True).exists()
    return JsonResponse({'existe_practica1': existe_practica1, 'existe_practica2': existe_practica2})

@estudiante_required
def dashboard(request):
    estudiante = Estudiante.objects.get(usuario=request.user)
    # Filtrar las solicitudes solo del estudiante actual
    total_solicitudes = InscripcionPractica.objects.filter(rut=estudiante.rut).count()
    solicitudes_pendientes = InscripcionPractica.objects.filter(rut=estudiante.rut, estado='Pendiente').count()
    solicitudes_aprobadas = InscripcionPractica.objects.filter(rut=estudiante.rut, estado='Aprobada').count()
    solicitudes_recientes = InscripcionPractica.objects.filter(rut=estudiante.rut).order_by('-id')[:5]

    context = {
        'total_solicitudes': total_solicitudes,
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_aprobadas': solicitudes_aprobadas,
        'solicitudes_recientes': solicitudes_recientes,
    }
    return render(request, 'dashboard.html', context)