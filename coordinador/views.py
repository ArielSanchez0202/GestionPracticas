import secrets
import string
from django.conf import settings
import pandas as pd
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import Estudiante
from django.http import HttpResponse
import openpyxl
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

def generar_contrasena(length=8):
    """Genera una contraseña aleatoria."""
    caracteres = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(caracteres) for _ in range(length))

def nuevo_coordinador(request):
    return render(request,'coordinador/nuevo_coordinador.html')

def agregar_estudiante(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        rut = request.POST.get('rut')
        domicilio = request.POST.get('domicilio')
        telefono = request.POST.get('telefono')
        carrera = request.POST.get('carrera')
        
        # Comprobar si el RUT ya está registrado
        if User.objects.filter(username=rut).exists():
            messages.error(request, "El RUT ya está registrado.")
            return redirect('coordinador:agregar_estudiante')

        try:
            # Generar una contraseña aleatoria
            contrasena = generar_contrasena()

            # Crear el usuario
            usuario = User.objects.create_user(username=rut, email=email, first_name=nombre)
            usuario.set_password(contrasena)
            usuario.save()

            # Asignar al grupo 'Estudiantes'
            grupo, _ = Group.objects.get_or_create(name='Estudiante')
            usuario.groups.add(grupo)

            # Crear el perfil del estudiante
            estudiante = Estudiante(
                usuario=usuario,
                rut=rut,
                domicilio=domicilio,
                carrera=carrera,
                numero_telefono=telefono  # Asegúrate de que este campo esté en tu modelo
            )
            estudiante.save()

            # Enviar el correo electrónico con las credenciales
            send_mail(
                'Credenciales de acceso',
                f'Hola {nombre},\n\nTu cuenta ha sido creada exitosamente.\n'
                f'Tu RUT: {rut}\nTu contraseña: {contrasena}\n\n'
                'Por favor, cambia tu contraseña después de iniciar sesión.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            messages.success(request, f"Estudiante '{nombre}' agregado exitosamente. Las credenciales han sido enviadas al correo.")
            return redirect('coordinador:listar_estudiantes')
        
        except Exception as e:
            messages.error(request, f"Error al agregar estudiante: {e}")
            return redirect('coordinador:agregar_estudiante')

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

                grupo, _ = Group.objects.get_or_create(name='Estudiante')
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

def editar_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)

    if request.method == 'POST':
        # Extraer los datos del formulario manualmente
        estudiante.usuario.first_name = request.POST.get('nombre')
        estudiante.usuario.email = request.POST.get('correo')
        estudiante.rut = request.POST.get('rut')
        estudiante.domicilio = request.POST.get('domicilio')
        estudiante.carrera = request.POST.get('carrera')

        # Guardar los cambios en el modelo Usuario y Estudiante
        estudiante.usuario.save()
        estudiante.save()

        return redirect('coordinador:listado_estudiantes')  # Redirige al listado de estudiantes después de editar

    return render(request, 'coordinador/editar_estudiante.html', {'estudiante': estudiante})

def detalle_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)

    return render(request, 'coordinador/detalle_estudiante.html', {'estudiante': estudiante})

#view coordinadores prueba
def coordinadores(request):
    # Tu lógica aquí
    return render(request, 'ver_coordinador.html')
