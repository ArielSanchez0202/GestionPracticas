import secrets
import string
from django.conf import settings
import pandas as pd
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from autenticacion.decorators import coordinador_required
from .models import Estudiante
from django.http import BadHeaderError, HttpResponse, JsonResponse
import openpyxl
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Coordinador
import uuid
import re
from smtplib import SMTPException
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.messages import get_messages

def generar_contrasena(length=8):
    """Genera una contraseña aleatoria."""
    caracteres = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(caracteres) for _ in range(length))

def validar_rut(rut):
    """Valida el RUT chileno en formato XXXXXXXX-X"""
    rut_pattern = re.compile(r'^\d{7,8}-[0-9kK]$')  # Formato sin puntos, con guión

    if not rut_pattern.match(rut):
        return False

    # Separar el número del dígito verificador
    numero, dv = rut.split("-")
    dv = dv.upper()

    # Validar dígito verificador
    suma = 0
    factor = 2
    for digit in reversed(numero):
        suma += int(digit) * factor
        factor = 9 if factor == 2 else factor - 1

    calculado_dv = 'K' if (11 - suma % 11 == 10) else str(11 - suma % 11 % 10)

    return dv == calculado_dv

from django.contrib import messages
import re

@coordinador_required
def agregar_estudiante(request):
    # Limpiar mensajes de la sesión para evitar que se acumulen en esta vista
    storage = get_messages(request)
    for _ in storage:
        pass

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        rut = request.POST.get('rut')
        domicilio = request.POST.get('domicilio')
        telefono = request.POST.get('telefono')
        carrera = request.POST.get('carrera')

        # Validación del formato de RUT
        rut_pattern = re.compile(r'^\d{7,8}-[0-9kK]$')
        if not rut_pattern.match(rut):
            return render(request, 'coordinador/agregar_estudiante.html', {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'rut': rut,
                'domicilio': domicilio,
                'telefono': telefono,
                'carrera': carrera
            })

        # Comprobar si el RUT ya está registrado
        if User.objects.filter(username=rut).exists():
            messages.error(request, "El RUT ya está registrado.")
            return render(request, 'coordinador/agregar_estudiante.html', {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'rut': rut,
                'domicilio': domicilio,
                'telefono': telefono,
                'carrera': carrera
            })

                # Comprobar si el RUT ya está registrado
        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado.")
            return render(request, 'coordinador/agregar_estudiante.html', {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'rut': rut,
                'domicilio': domicilio,
                'telefono': telefono,
                'carrera': carrera
            })

        try:
            contrasena = generar_contrasena()

            usuario = User.objects.create_user(username=rut, email=email, first_name=nombre, last_name=apellido)
            usuario.set_password(contrasena)
            usuario.save()

            grupo, _ = Group.objects.get_or_create(name='Estudiante')
            usuario.groups.add(grupo)

            estudiante = Estudiante(
                usuario=usuario,
                rut=rut,
                domicilio=domicilio,
                carrera=carrera,
                numero_telefono=telefono
            )
            estudiante.save()

            send_mail(
                'Credenciales de acceso',
                f'Hola {nombre},\n\nTu cuenta ha sido creada exitosamente.\n'
                f'Tu RUT: {rut}\nTu contraseña: {contrasena}\n\n'
                'Por favor, cambia tu contraseña después de iniciar sesión.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            # Guarda el mensaje en la sesión para mostrarlo en `listar_estudiantes`
            request.session['message_success'] = f"Estudiante '{nombre} {apellido}' agregado exitosamente. Las credenciales han sido enviadas al correo."
            return redirect('coordinador:listar_estudiantes')

        except BadHeaderError:
            messages.error(request, "Cabecera del correo inválida.")
        except SMTPException as smtp_error:
            messages.error(request, f"Error al enviar el correo: {smtp_error}")
        except Exception as e:
            messages.error(request, f"Error al agregar estudiante: {e}")

        # Renderizar la página en caso de error
        return render(request, 'coordinador/agregar_estudiante.html', {
            'nombre': nombre,
            'apellido': apellido,
            'email': email,
            'rut': rut,
            'domicilio': domicilio,
            'telefono': telefono,
            'carrera': carrera
        })

    # Si es GET, renderizar la página sin procesamiento de formulario
    return render(request, 'coordinador/agregar_estudiante.html')

@coordinador_required
def carga_masiva_estudiantes(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        if not archivo:
            messages.error(request, "Por favor, selecciona un archivo.")
            return redirect('coordinador:carga_masiva_estudiantes')

        try:
            df = pd.read_excel(archivo, engine='openpyxl')
            df.columns = ['Nombre','Apellido','RUT','Domicilio','numero_telefono','CorreoElectronico', 'Carrera']

            estudiantes = df.to_dict(orient='records')
            request.session['alumnos_preview'] = estudiantes
            return render(request, 'coordinador/carga_masiva_estudiantes.html', {'estudiantes': estudiantes})
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {e}")
            return redirect('coordinador:carga_masiva_estudiantes')
    return render(request, 'coordinador/carga_masiva_estudiantes.html')

@coordinador_required
def previsualizar_estudiantes(request):
    alumnos = request.session.get('alumnos_preview', [])
    if request.method == 'POST':
        for alumno in alumnos:
            rut = alumno['RUT']
            apellido = alumno['Apellido']
            email = alumno['CorreoElectronico']
            nombre = alumno['Nombre']
            domicilio = alumno['Domicilio']
            numero_telefono = alumno['numero_telefono']
            carrera = alumno['Carrera']

            if not User.objects.filter(username=rut).exists():
                usuario = User.objects.create_user(username=rut, email=email, first_name=nombre, last_name=apellido)
                usuario.set_password('password123')
                usuario.save()

                grupo, _ = Group.objects.get_or_create(name='Estudiante')
                usuario.groups.add(grupo)

                estudiante = Estudiante(
                    usuario=usuario,
                    rut=rut,
                    numero_telefono=numero_telefono,
                    domicilio=domicilio,
                    carrera=carrera
                )
                estudiante.save()

        request.session.pop('alumnos_preview', None)
        messages.success(request, "Estudiantes añadidos exitosamente.")
        return redirect('coordinador:listar_estudiantes')
    return render(request, 'coordinador/carga_masiva_preview.html', {'alumnos': alumnos})

@coordinador_required
def descargar_plantilla_estudiantes(request):
    columnas = ['Nombre','Apellido','Rut','Domicilio','numero_telefono', 'Correo Electrónico','Carrera']
    df = pd.DataFrame(columns=columnas)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=plantilla_estudiantes.xlsx'
    df.to_excel(response, index=False, engine='openpyxl')
    return response


@coordinador_required
def listar_estudiantes(request):
    estudiantes = Estudiante.objects.all()

    # Recuperar el mensaje de éxito y eliminarlo de la sesión
    message_success = request.session.pop('message_success', None)
    if message_success:
        messages.success(request, message_success)

    return render(request, 'coordinador/listar_estudiantes.html', {'estudiantes': estudiantes})

def coordinadores(request):
    return render(request,'coordinador/coordinadores.html')

def listar_coordinador(request):
    coordinadores = Coordinador.objects.all()
    return render(request,'coordinador/listar_coordinador.html',{'coordinadores':coordinadores})

def crear_coordinador(request):
    usuarios = Coordinador.objects.all()
    return render(request,'coordinador/crear_coordinador.html',{'usuarios':usuarios})

def registrar_coordinador(request):
    if request.method == 'POST':
        nombre = request.POST.get("txtnombre")
        apellido = request.POST.get("txtapellido")
        rut = request.POST.get("txtrut")
        domicilio = request.POST.get("txtdomicilio")
        carrera = request.POST.get("txtcarrera")
        
        # Obtén la instancia completa del usuario usando su ID
        
        
        # Guarda el nuevo coordinador, asociándolo con el usuario
        coordinador = Coordinador.objects.create(
            nombre=nombre, 
            apellido=apellido,
            rut=rut,
            domicilio=domicilio,
            carrera=carrera
        )
        
        return redirect('coordinador:listar_coordinador')

def editar_coordinador(request,rut):
    usuario = Coordinador.objects.get(rut=rut)
    return render(request,"coordinador/editar_coordinador.html",{'usuario':usuario})

def editarcoordinador(request):
        nombre = request.POST.get("txtnombre")
        apellido = request.POST.get("txtapellido")
        rut = request.POST.get("txtrut")
        domicilio = request.POST.get("txtdomicilio")
        carrera = request.POST.get("txtcarrera")

        usuario = Coordinador.objects.get(rut=rut)
        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.domicilio = domicilio
        usuario.carrera = carrera
        usuario.save()

        return redirect('coordinador:listar_coordinador')
        
@coordinador_required
def editar_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, usuario_id=estudiante_id)

    if request.method == 'POST':
        estudiante.usuario.first_name = request.POST.get('nombre')
        estudiante.usuario.last_name = request.POST.get('apellido')
        estudiante.usuario.email = request.POST.get('correo')
        estudiante.rut = request.POST.get('rut')
        estudiante.domicilio = request.POST.get('domicilio')
        estudiante.numero_telefono = request.POST.get('numero_telefono')  # Agregar número de teléfono
        estudiante.carrera = request.POST.get('carrera')

        estudiante.usuario.save()
        estudiante.save()

        return redirect('coordinador:listar_estudiantes')

    return render(request, 'coordinador/editar_estudiante.html', {'estudiante': estudiante})

@coordinador_required
def detalle_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, usuario_id=estudiante_id)

    return render(request, 'coordinador/detalle_estudiante.html', {'estudiante': estudiante})

#view coordinadores prueba
def coordinadores(request):
    # Tu lógica aquí
    return render(request, 'ver_coordinador.html')

@coordinador_required
def verificar_rut(request):
    rut = request.GET.get('rut')
    existe = User.objects.filter(username=rut).exists()
    return JsonResponse({'existe': existe})