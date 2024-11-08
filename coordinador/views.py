import secrets
import string
from django.conf import settings
import pandas as pd
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from autenticacion.decorators import coordinador_required
from .models import Estudiante
from django.http import BadHeaderError, HttpResponse, HttpResponseNotFound, JsonResponse
import openpyxl
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Coordinador
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

        # Verificar si el correo ya está registrado
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

            # Crear usuario
            usuario = User.objects.create_user(username=rut, email=email, first_name=nombre, last_name=apellido)
            usuario.set_password(contrasena)
            usuario.save()

            # Asignar grupo
            grupo, _ = Group.objects.get_or_create(name='Estudiante')
            usuario.groups.add(grupo)

            # Crear estudiante
            estudiante = Estudiante(
                usuario=usuario,
                rut=rut,
                domicilio=domicilio,
                carrera=carrera,
                numero_telefono=telefono
            )
            estudiante.save()

            # Intentar enviar el correo
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
            return redirect('listar_estudiantes')

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
            return redirect('carga_masiva_estudiantes')

        try:
            df = pd.read_excel(archivo, engine='openpyxl')
            df.columns = ['Nombre','Apellido','RUT','Domicilio','numero_telefono','CorreoElectronico', 'Carrera']

            estudiantes = df.to_dict(orient='records')
            request.session['alumnos_preview'] = estudiantes
            return render(request, 'coordinador/carga_masiva_estudiantes.html', {'estudiantes': estudiantes})
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {e}")
            return redirect('carga_masiva_estudiantes')
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
        return redirect('listar_estudiantes')
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
    # Obtener el estado de la URL o establecerlo en "activo" por defecto
    estado = request.GET.get('estado', 'activo')

    # Filtrar estudiantes según el atributo is_active de su usuario
    if estado == 'activo':
        estudiantes = Estudiante.objects.filter(usuario__is_active=True)
    elif estado == 'inactivo':
        estudiantes = Estudiante.objects.filter(usuario__is_active=False)
    else:
        estudiantes = Estudiante.objects.all()  # Para mostrar todos si 'estado' es 'Todos'

    context = {
        'estudiantes': estudiantes,
    }
    return render(request, 'coordinador/listar_estudiantes.html', context)

def coordinadores(request):
    return render(request,'coordinador/coordinadores.html')

def listar_coordinador(request):
    coordinadores = Coordinador.objects.all()
    return render(request,'coordinador/listar_coordinador.html',{'coordinadores':coordinadores})

def crear_coordinador(request):
    usuarios = Coordinador.objects.all()
    return render(request,'coordinador/crear_coordinador.html',{'usuarios':usuarios})

def registrar_coordinador(request):
    # Limpiar mensajes de la sesión para evitar acumulaciones
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
            messages.error(request, "El RUT ingresado no es válido.")
            return render(request, 'coordinador/crear_coordinador.html', {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'rut': rut,
                'domicilio': domicilio,
                'telefono': telefono,
                'carrera':carrera,
            })

        # Comprobar si el RUT ya está registrado
        if User.objects.filter(username=rut).exists():
            messages.error(request, "El RUT ya está registrado.")
            return render(request, 'coordinador/crear_coordinador.html', {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'rut': rut,
                'domicilio': domicilio,
                'telefono': telefono,
                'carrera':carrera,
            })

        # Verificar si el correo ya está registrado
        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado.")
            return render(request, 'coordinador/crear_coordinador.html', {
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'rut': rut,
                'domicilio': domicilio,
                'telefono': telefono,
                'carrera':carrera,
            })

        try:
            contrasena = generar_contrasena()

            # Crear usuario
            usuario = User.objects.create_user(username=rut, email=email, first_name=nombre, last_name=apellido)
            usuario.set_password(contrasena)
            usuario.save()

            # Asignar al grupo "Coordinador"
            grupo, _ = Group.objects.get_or_create(name='Coordinador')
            usuario.groups.add(grupo)

            # Crear Coordinador
            coordinador = Coordinador(
                usuario=usuario,
                rut=rut,
                domicilio=domicilio,
                numero_telefono=telefono,
                carrera=carrera,
            )
            coordinador.save()

            # Enviar credenciales por correo
            send_mail(
                'Credenciales de acceso',
                f'Hola {nombre},\n\nTu cuenta de coordinador ha sido creada exitosamente.\n'
                f'Tu RUT: {rut}\nTu contraseña: {contrasena}\n\n'
                'Por favor, cambia tu contraseña después de iniciar sesión.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            # Guardar mensaje de éxito en la sesión y redirigir
            request.session['message_success'] = f"Coordinador '{nombre} {apellido}' agregado exitosamente. Las credenciales han sido enviadas al correo."
            return redirect('listar_coordinadores')

        except BadHeaderError:
            messages.error(request, "Cabecera del correo inválida.")
        except SMTPException as smtp_error:
            messages.error(request, f"Error al enviar el correo: {smtp_error}")
        except Exception as e:
            messages.error(request, f"Error al agregar coordinador: {e}")

        # Renderizar la página en caso de error
        return render(request, 'coordinador/crear_coordinador.html', {
            'nombre': nombre,
            'apellido': apellido,
            'email': email,
            'rut': rut,
            'domicilio': domicilio,
            'telefono': telefono,
            'carrera':carrera,
        })

    # Renderizar la página si el método es GET
    return render(request, 'coordinador/crear_coordinador.html')
@coordinador_required
def editar_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, usuario_id=estudiante_id)
    usuario = estudiante.usuario  # Debe ser una instancia de User

    # Limpiar mensajes de la sesión
    storage = get_messages(request)
    for _ in storage:
        pass

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('correo')
        rut = request.POST.get('rut')
        domicilio = request.POST.get('domicilio')
        telefono = request.POST.get('numero_telefono')
        carrera = request.POST.get('carrera')

        # Validación del formato de RUT
        rut_pattern = re.compile(r'^\d{7,8}-[0-9kK]$')
        if not rut_pattern.match(rut):
            messages.error(request, "El formato del RUT es inválido.")
            return render(request, 'coordinador/editar_estudiante.html', {
                'estudiante': estudiante,
                'nombre': nombre,
                'apellido': apellido,
                'correo': email,
                'rut': rut,
                'domicilio': domicilio,
                'numero_telefono': telefono,
                'carrera': carrera
            })

        # Comprobar si el RUT ya está registrado por otro estudiante
        if User.objects.filter(username=rut).exclude(pk=usuario.pk).exists():
            messages.error(request, "El RUT ya está registrado.")
            return render(request, 'coordinador/editar_estudiante.html', {
                'estudiante': estudiante,
                'nombre': nombre,
                'apellido': apellido,
                'correo': email,
                'rut': rut,
                'domicilio': domicilio,
                'numero_telefono': telefono,
                'carrera': carrera
            })

        # Verificar si el correo ya está registrado por otro estudiante
        if User.objects.filter(email=email).exclude(pk=usuario.pk).exists():
            messages.error(request, "El correo ya está registrado.")
            return render(request, 'coordinador/editar_estudiante.html', {
                'estudiante': estudiante,
                'nombre': nombre,
                'apellido': apellido,
                'correo': email,
                'rut': rut,
                'domicilio': domicilio,
                'numero_telefono': telefono,
                'carrera': carrera
            })

        try:
            # Actualizar datos del usuario
            usuario.first_name = nombre
            usuario.last_name = apellido
            usuario.email = email
            usuario.username = rut
            usuario.save()

            # Actualizar datos del estudiante
            estudiante.rut = rut
            estudiante.domicilio = domicilio
            estudiante.numero_telefono = telefono
            estudiante.carrera = carrera
            estudiante.save()

            messages.success(request, f"Estudiante '{nombre} {apellido}' actualizado exitosamente.")
            return redirect('listar_estudiantes')

        except Exception as e:
            messages.error(request, f"Error al actualizar estudiante: {e}")

    # Si es GET, renderizar la página sin procesamiento de formulario
    return render(request, 'coordinador/editar_estudiante.html', {
        'estudiante': estudiante,
    })

def editar_coordinador(request, coordinador_id):
    # Obtener el objeto Coordinador o retornar 404 si no existe
    coordinador = get_object_or_404(Coordinador, usuario_id=coordinador_id)
    usuario = coordinador.usuario  # Debe ser una instancia de User

    # Limpiar mensajes de la sesión
    storage = get_messages(request)
    for _ in storage:
        pass

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('correo')
        rut = request.POST.get('rut')
        domicilio = request.POST.get('domicilio')
        telefono = request.POST.get('numero_telefono')

        # Validación del formato de RUT
        rut_pattern = re.compile(r'^\d{7,8}-[0-9kK]$')
        if not rut_pattern.match(rut):
            messages.error(request, "El formato del RUT es inválido.")
            return render(request, 'coordinador/editar_coordinador.html', {
                'coordinador': coordinador,
                'nombre': nombre,
                'apellido': apellido,
                'correo': email,
                'rut': rut,
                'domicilio': domicilio,
                'numero_telefono': telefono,
            })

        # Comprobar si el RUT ya está registrado por otro coordinador
        if User.objects.filter(username=rut).exclude(pk=usuario.pk).exists():
            messages.error(request, "El RUT ya está registrado.")
            return render(request, 'coordinador/editar_coordinador.html', {
                'coordinador': coordinador,
                'nombre': nombre,
                'apellido': apellido,
                'correo': email,
                'rut': rut,
                'domicilio': domicilio,
                'numero_telefono': telefono,
            })

        # Verificar si el correo ya está registrado por otro coordinador
        if User.objects.filter(email=email).exclude(pk=usuario.pk).exists():
            messages.error(request, "El correo ya está registrado.")
            return render(request, 'coordinador/editar_coordinador.html', {
                'coordinador': coordinador,
                'nombre': nombre,
                'apellido': apellido,
                'correo': email,
                'rut': rut,
                'domicilio': domicilio,
                'numero_telefono': telefono,
            })

        try:
            # Actualizar datos del usuario
            usuario.first_name = nombre
            usuario.last_name = apellido
            usuario.email = email
            usuario.username = rut
            usuario.save()

            # Actualizar datos del coordinador
            coordinador.rut = rut
            coordinador.domicilio = domicilio
            coordinador.numero_telefono = telefono
            coordinador.save()

            messages.success(request, f"Coordinador '{nombre} {apellido}' actualizado exitosamente.")

        except Exception as e:
            messages.error(request, f"Error al actualizar coordinador: {e}")

    # Si es GET, renderizar la página sin procesamiento de formulario
    return render(request, 'coordinador/editar_coordinador.html', {
        'coordinador': coordinador,
    })

def ver_coordinador(request, coordinador_id):
    coordinadores = get_object_or_404(Coordinador, usuario_id=coordinador_id)

    return render(request, 'coordinador/ver_coordinador.html', {'coordinadores': coordinadores})
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


@coordinador_required
def solicitudes_practica(request):
    return render(request, 'coordinador/solicitudes_practicas.html')

@coordinador_required
def informes_avances(request):
    return render(request, 'coordinador/informes_avances.html')

@coordinador_required
def autoevaluaciones(request):
    return render(request, 'coordinador/autoevaluaciones.html')

@coordinador_required
def informes_finales(request):
    return render(request, 'coordinador/informes_finales.html')

@coordinador_required
def documentos(request):
    return render(request, 'coordinador/documentos.html')
