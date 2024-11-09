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
    practicas = InscripcionPractica.objects.all()  # O filtra por estudiante si es necesario
    context = {
        'practicas': practicas,
    }
    return render(request, 'estudiante.html', context)

@estudiante_required
def inscripcion_practica_view(request):
    if request.method == 'POST':
        # Recuperar los datos enviados por el formulario
        nombre_completo = request.POST.get('nombre_completo')
        rut = request.POST.get('rut')
        domicilio = request.POST.get('domicilio')
        telefono = request.POST.get('telefono')
        correo = request.POST.get('correo')
        carrera = request.POST.get('carrera')
        practica1 = request.POST.get('practica1') == 'on'  # checkbox
        practica2 = request.POST.get('practica2') == 'on'  # checkbox
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
            nombre_completo=nombre_completo,
            rut=rut,
            domicilio=domicilio,
            telefono=telefono,
            correo=correo,
            carrera=carrera,
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
            # Manejar el error (puedes agregar un mensaje de error para mostrar en la plantilla)
            print(f'Error al guardar: {e}')

        # Redirigir a estudiante.html después de enviar el formulario exitosamente
        return redirect('estudiantes_main')

    return render(request, 'inscripcion_practica.html')

@estudiante_required
def verificar_practica1(request):
    existe_practica1 = InscripcionPractica.objects.filter(practica1=True).exists()
    return JsonResponse({'existe_practica1': existe_practica1})
@coordinador_required
def listar_practicas(request):
    # Obtener todas las inscripciones de prácticas
    inscripciones = InscripcionPractica.objects.all()
    return render(request, 'listar_practicas.html', {'inscripciones': inscripciones})

@coordinador_required
def ver_formulario(request, solicitud_id):
    # Obtener la solicitud de práctica específica por su ID
    solicitud = get_object_or_404(InscripcionPractica, pk=solicitud_id)
    
    # Renderizar el template y pasar la solicitud al contexto
    return render(request, 'ver_formulario.html', {'solicitud': solicitud})