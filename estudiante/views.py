from django.shortcuts import render, redirect, get_object_or_404
from autenticacion.decorators import estudiante_required
from coordinador.models import Estudiante, Practica
from django.utils import timezone

# Create your views here.
def estudiantes_main(request):
    return render(request, 'estudiantes_main.html')

@estudiante_required
def listar_practicas(request):
    practicas = Practica.objects.all()
    return render(request, 'estudiantes/listar_practicas.html', {'practicas': practicas})

@estudiante_required
def agregar_practica(request):
    if request.method == 'POST':
        # Obtener el estudiante autenticado
        estudiante = get_object_or_404(Estudiante, usuario=request.user)

        # Datos de la práctica
        practica_tipo = request.POST.get('practica_tipo')
        rut = request.POST.get('rut')
        domicilio = request.POST.get('domicilio')
        telefono = request.POST.get('telefono')
        carrera = request.POST.get('carrera')
        
        # Datos de la empresa
        razon_social = request.POST.get('razon_social')
        direccion_empresa = request.POST.get('direccion_empresa')
        jefe_directo = request.POST.get('jefe_directo')
        cargo = request.POST.get('cargo')
        telefono_empresa = request.POST.get('telefono_empresa')
        email_empresa = request.POST.get('email_empresa')
        
        # Fechas de la práctica
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_termino = request.POST.get('fecha_termino')
        
        # Crear nueva inscripción de práctica
        practica = Practica(
            estudiante=estudiante,
            tipo_practica=practica_tipo,
            rut=rut,
            domicilio=domicilio,
            telefono=telefono,
            carrera=carrera,
            razon_social=razon_social,
            direccion_empresa=direccion_empresa,
            jefe_directo=jefe_directo,
            cargo=cargo,
            telefono_empresa=telefono_empresa,
            email_empresa=email_empresa,
            fecha_inicio=fecha_inicio,
            fecha_termino=fecha_termino
        )
        practica.save()

        # Redirigir después de guardar
        return redirect('estudiante:listar_practicas')

    return render(request, 'estudiante/agregar_practica.html')