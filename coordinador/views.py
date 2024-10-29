import pandas as pd
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Estudiante
from django.http import HttpResponse
import openpyxl
from django.contrib.auth.decorators import login_required

def agregar_estudiante(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        rut = request.POST.get('rut')
        domicilio = request.POST.get('domicilio')
        telefono = request.POST.get('telefono')
        carrera = request.POST.get('carrera')
        
        if User.objects.filter(username=rut).exists():
            messages.error(request, "El RUT ya está registrado.")
            return redirect('coordinador:agregar_estudiante')

        usuario = User.objects.create_user(username=rut, email=email, first_name=nombre)
        usuario.set_password('password123')
        usuario.save()

        grupo, _ = Group.objects.get_or_create(name='Estudiantes')
        usuario.groups.add(grupo)

        estudiante = Estudiante(
            usuario=usuario,
            rut=rut,
            domicilio=domicilio,
            carrera=carrera
        )
        estudiante.save()

        messages.success(request, "Estudiante agregado exitosamente.")
        return redirect('coordinador:listar_estudiantes')
    return render(request, 'coordinador/agregar_estudiante.html')


def carga_masiva_estudiantes(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        if not archivo:
            messages.error(request, "Por favor, selecciona un archivo.")
            return redirect('coordinador:carga_masiva_estudiantes')

        try:
            df = pd.read_excel(archivo, engine='openpyxl')
            df.columns = ['Nombre', 'CorreoElectronico', 'RUT', 'Domicilio', 'Carrera']

            estudiantes = df.to_dict(orient='records')
            request.session['alumnos_preview'] = estudiantes
            return render(request, 'coordinador/carga_masiva_estudiantes.html', {'estudiantes': estudiantes})
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {e}")
            return redirect('coordinador:carga_masiva_estudiantes')
    return render(request, 'coordinador/carga_masiva_estudiantes.html')


def previsualizar_estudiantes(request):
    alumnos = request.session.get('alumnos_preview', [])
    if request.method == 'POST':
        for alumno in alumnos:
            rut = alumno['RUT']
            email = alumno['CorreoElectronico']
            nombre = alumno['Nombre']
            domicilio = alumno['Domicilio']
            carrera = alumno['Carrera']

            if not User.objects.filter(username=rut).exists():
                usuario = User.objects.create_user(username=rut, email=email, first_name=nombre)
                usuario.set_password('password123')
                usuario.save()

                grupo, _ = Group.objects.get_or_create(name='Estudiantes')
                usuario.groups.add(grupo)

                estudiante = Estudiante(
                    usuario=usuario,
                    rut=rut,
                    domicilio=domicilio,
                    carrera=carrera
                )
                estudiante.save()

        request.session.pop('alumnos_preview', None)
        messages.success(request, "Estudiantes añadidos exitosamente.")
        return redirect('coordinador:listar_estudiantes')
    return render(request, 'coordinador/carga_masiva_preview.html', {'alumnos': alumnos})


def descargar_plantilla_estudiantes(request):
    columnas = ['Nombre', 'Correo Electrónico', 'RUT', 'Domicilio', 'Carrera']
    df = pd.DataFrame(columns=columnas)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=plantilla_estudiantes.xlsx'
    df.to_excel(response, index=False, engine='openpyxl')
    return response


#@login_required
def listar_estudiantes(request):
    estudiantes = Estudiante.objects.all()
    return render(request, 'coordinador/listar_estudiantes.html', {'estudiantes': estudiantes})
