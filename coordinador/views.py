import locale
import re
import secrets
import string
from datetime import datetime, timezone
from smtplib import SMTPException
from django.forms import ValidationError
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.messages import get_messages
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.http import BadHeaderError, HttpResponse, HttpResponseNotFound, JsonResponse, FileResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.urls import reverse
from django.utils.http import urlencode
import json
import logging
from django.shortcuts import get_object_or_404, render, redirect
from autenticacion.decorators import coordinador_required
from .forms import DocumentForm, InformeConfidencialForm
from .models import Coordinador, Document, Estudiante, InformeConfidencial, Notificacion, PracticaConfig, FichaInscripcion, Autoevaluacion, FormularioToken, Practica, InformeAvances, Rubrica
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from .models import *
from decimal import Decimal, InvalidOperation
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
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
            # Leer archivo Excel
            df = pd.read_excel(archivo, engine='openpyxl')

            # Definir los encabezados correctos
            columnas_esperadas = ['Nombre', 'Apellido', 'Rut', 'Domicilio', 'numero_telefono', 'CorreoElectronico', 'Carrera']
            
            # Verificar que el archivo tenga las mismas columnas
            if list(df.columns) != columnas_esperadas:
                messages.error(request, "El archivo no tiene las columnas correctas. Por favor, descarga la plantilla y vuelve a intentar.")
                return redirect('carga_masiva_estudiantes')

            # Validar que no haya casillas vacías
            for index, row in df.iterrows():
                if row.isnull().any():  # Verifica si hay algún valor nulo en la fila
                    messages.error(request, f"Fila {index + 1} tiene campos vacíos. Por favor, completa todos los campos.")
                    return redirect('carga_masiva_estudiantes')

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
    mensajes_error = []

    def validar_rut2(rut):
        """Valida que el RUT tenga el formato correcto y sea real."""
        # Verifica el formato (8 dígitos, guion y dígito verificador)
        if not re.fullmatch(r'^\d{7,8}-[0-9Kk]$', rut):
            return False
        
        # Separar el número y el dígito verificador
        cuerpo, dv = rut[:-2], rut[-1].upper()
        
        # Calcular el dígito verificador
        suma = 0
        multiplicador = 2

        for digito in reversed(cuerpo):
            suma += int(digito) * multiplicador
            multiplicador = 2 if multiplicador == 7 else multiplicador + 1
        
        # Calcular el dígito verificador esperado
        resto = suma % 11
        digito_calculado = 'K' if resto == 1 else '0' if resto == 0 else str(11 - resto)
        
        return dv == digito_calculado

    if request.method == 'POST':
        for alumno in alumnos:
            rut = alumno['Rut']
            apellido = alumno['Apellido']
            email = alumno['CorreoElectronico']
            nombre = alumno['Nombre']
            domicilio = alumno['Domicilio']
            numero_telefono = alumno['numero_telefono']
            carrera = alumno['Carrera']
            
            # Validar el formato y la autenticidad del RUT
            if not validar_rut2(rut):
                mensajes_error.append(f"El RUT {rut} no tiene el formato correcto o no es un RUT válido.")
                continue
            
            # Validar formato del teléfono (debe comenzar con 9 y tener 9 dígitos)
            if not re.fullmatch(r'^9\d{8}$', str(numero_telefono)):
                mensajes_error.append(f"El número de teléfono {numero_telefono} no es válido. Debe comenzar con 9 y tener 9 dígitos.")
                continue
            
            # Validar formato del correo electrónico
            if not re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                mensajes_error.append(f"El correo {email} no tiene un formato válido.")
                continue
            
            # Validar si el RUT ya está registrado
            if User.objects.filter(username=rut).exists():
                mensajes_error.append(f"El RUT {rut} ya está registrado.")
                continue
            
            # Validar si el correo ya está registrado
            if User.objects.filter(email=email).exists():
                mensajes_error.append(f"El correo {email} ya está registrado.")
                continue
            
            # Si el RUT no está registrado, crear el usuario y estudiante
            contrasena = generar_contrasena()
            usuario = User.objects.create_user(username=rut, email=email, first_name=nombre, last_name=apellido)
            usuario.set_password(contrasena)
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

            # Enviar el correo con las credenciales
            try:
                send_mail(
                    'Credenciales de acceso',
                    f'Hola {nombre},\n\nTu cuenta ha sido creada exitosamente.\n'
                    f'Tu RUT: {rut}\nTu contraseña: {contrasena}\n\n'
                    'Por favor, cambia tu contraseña después de iniciar sesión.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                # Manejo de excepciones al enviar el correo
                messages.error(request, f"Error al enviar el correo a {email}: {e}")

        # Si hubo errores, mostramos los mensajes
        if mensajes_error:
            for mensaje in mensajes_error:
                messages.error(request, mensaje)
        else:
            messages.success(request, "Estudiantes añadidos exitosamente y se han enviado las credenciales al correo.")

        request.session.pop('alumnos_preview', None)
        return redirect('listar_estudiantes')
    
    return render(request, 'coordinador/carga_masiva_preview.html', {'alumnos': alumnos})

@coordinador_required
def descargar_plantilla_estudiantes(request):
    columnas = ['Nombre','Apellido','Rut','Domicilio','numero_telefono', 'CorreoElectronico','Carrera']
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

@coordinador_required
def coordinadores(request):
    return render(request,'coordinador/coordinadores.html')

@coordinador_required
def listar_coordinador(request):
    coordinadores = Coordinador.objects.all()
    return render(request,'coordinador/listar_coordinador.html',{'coordinadores':coordinadores})

@coordinador_required
def crear_coordinador(request):
    usuarios = Coordinador.objects.all()
    return render(request,'coordinador/crear_coordinador.html',{'usuarios':usuarios})

@coordinador_required
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
            return redirect('listar_coordinador')

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

@coordinador_required
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

@coordinador_required
def ver_coordinador(request, coordinador_id):
    coordinadores = get_object_or_404(Coordinador, usuario_id=coordinador_id)

    return render(request, 'coordinador/ver_coordinador.html', {'coordinadores': coordinadores})

@coordinador_required
def detalle_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, usuario__id=estudiante_id)

    # Obtener las prácticas y sus fichas asociadas
    practicas = estudiante.practicas.all()
    fichas_inscripcion = FichaInscripcion.objects.filter(practica__in=practicas)

    context = {
        'estudiante': estudiante,
        'fichas_inscripcion': fichas_inscripcion,  # Lista de fichas para usarlas en el template
    }

    return render(request, 'coordinador/detalle_estudiante.html', context)

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
def informes_avances(request):
    # Filtrar solo las fichas aprobadas y que tienen un informe de avance asociado
    fichas_aprobadas = FichaInscripcion.objects.filter(estado="Aprobada").select_related('estudiante__usuario', 'practica')

    # Filtramos para solo incluir las que tienen informe de avances subido
    fichas_info = []
    for ficha in fichas_aprobadas:
        if ficha.practica and ficha.practica.informeavances_set.exists():
            # Calcular el estado basado en el informe de avance
            estado = "Entregado" if ficha.practica.informeavances_set.last().nota_avance else "Pendiente de entrega"

            # Agregar la ficha con el estado calculado
            fichas_info.append({
                "ficha": ficha,
                "estado": estado,
            })

    return render(request, 'coordinador/informes_avances.html', {"fichas_info": fichas_info})


@coordinador_required
def autoevaluaciones(request):
    # Obtener los RUT de los estudiantes activos
    estudiantes_activos = Estudiante.objects.filter(usuario__is_active=True).values_list('rut', flat=True)

    # Filtrar inscripciones de estudiantes activos con autoevaluaciones completadas
    inscripciones = FichaInscripcion.objects.filter(
        estudiante__rut__in=estudiantes_activos,
        practica__autoevaluacion__isnull=False  # Solo inscripciones con autoevaluaciones asociadas
    ).distinct()  # Aseguramos que no haya duplicados

    # Filtrar autoevaluaciones asociadas a las inscripciones seleccionadas
    autoevaluaciones = Autoevaluacion.objects.filter(
        practica__fichainscripcion__in=inscripciones
    )

    return render(request, 'coordinador/autoevaluaciones.html', {
        'inscripciones': inscripciones,
        'autoevaluaciones': autoevaluaciones,
    })

@coordinador_required
def actualizar_nota(request):
    if request.method == 'POST':
        practica_id = request.POST.get('practica_id')
        nueva_nota = request.POST.get('nota', '').replace(',', '.')  # Cambiar coma a punto

        try:
            nota_decimal = Decimal(nueva_nota)  # Convertir a Decimal
        except InvalidOperation:
            messages.error(request, "La nota ingresada no es válida. Por favor, usa un número válido.")
            return redirect('autoevaluaciones')  # Redirige en caso de error

        try:
            autoevaluacion = Autoevaluacion.objects.get(practica_id=practica_id)
            autoevaluacion.nota = nota_decimal
            autoevaluacion.save()
            messages.success(request, "Nota actualizada con éxito.")
        except Autoevaluacion.DoesNotExist:
            messages.error(request, "Error: No se encontró la autoevaluación.")

        return redirect('autoevaluaciones')  # Redirige tras actualizar
    return redirect('autoevaluaciones')  # Manejo de métodos no POST

def actualizar_nota_informe_confidencial(request):
    if request.method == 'POST':
        practica_id = request.POST.get('practica_id')
        nueva_nota = request.POST.get('nota', '').replace(',', '.')  # Cambiar coma a punto

        try:
            nota_decimal = Decimal(nueva_nota)  # Convertir a Decimal
        except InvalidOperation:
            messages.error(request, "La nota ingresada no es válida. Por favor, usa un número válido.")
            return redirect('informes_confidenciales')  # Redirige en caso de error

        try:
            informe = InformeConfidencial.objects.get(practica_id=practica_id)
            informe.nota = nota_decimal
            informe.save()
            messages.success(request, "Nota del informe confidencial actualizada con éxito.")
        except InformeConfidencial.DoesNotExist:
            messages.error(request, "Error: No se encontró el informe confidencial.")

        return redirect('listado_informes_confidenciales')  # Redirige tras actualizar
  # Manejo de métodos no POST

@coordinador_required
def revisar_autoevaluacion(request, practica_id):
    # Recuperar la FichaInscripcion asociada
    ficha_inscripcion = get_object_or_404(FichaInscripcion, id=practica_id)

    # Acceder a la instancia de Practica desde FichaInscripcion
    practica = ficha_inscripcion.practica

    # Obtener la autoevaluación asociada a la práctica
    autoevaluacion = Autoevaluacion.objects.filter(practica=practica).first()

    # Renderizar la plantilla con los datos del estudiante, la práctica y la autoevaluación
    context = {
        'estudiante': ficha_inscripcion.estudiante,  # Datos del estudiante desde FichaInscripcion
        'solicitud': ficha_inscripcion,              # Información sobre la solicitud (cargo, empresa, etc.)
        'autoevaluacion': autoevaluacion,            # Autoevaluación asociada a la práctica
    }

    return render(request, 'coordinador/revisar_autoevaluacion.html', context)

@coordinador_required
def informes_finales(request):
    return render(request, 'coordinador/informes_finales.html')

@coordinador_required
def dashboard(request):
    total_solicitudes = FichaInscripcion.objects.count()
    solicitudes_pendientes = FichaInscripcion.objects.filter(estado='Pendiente').count()
    solicitudes_aprobadas = FichaInscripcion.objects.filter(estado='Aprobada').count()
    solicitudes_recientes = FichaInscripcion.objects.order_by('-id')[:5]  # Últimas 5 solicitudes

    context = {
        'total_solicitudes': total_solicitudes,
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_aprobadas': solicitudes_aprobadas,
        'solicitudes_recientes': solicitudes_recientes,
    }
    return render(request, 'coordinador/dashboard.html', context)

@coordinador_required
def listar_practicas(request):
    # Obtener los RUT de los estudiantes activos
    estudiantes_activos = Estudiante.objects.filter(usuario__is_active=True).values_list('rut', flat=True)
    
    # Filtrar inscripciones solo para estudiantes con esos RUT
    inscripciones = FichaInscripcion.objects.filter(estudiante__rut__in=estudiantes_activos)
    
    return render(request, 'coordinador/listar_practicas.html', {'inscripciones': inscripciones})

@coordinador_required
def ver_formulario(request, solicitud_id):
    # Obtener la solicitud de práctica específica por su ID
    solicitud = get_object_or_404(FichaInscripcion, pk=solicitud_id)

    # Obtener los datos del estudiante relacionado con la solicitud
    estudiante = solicitud.estudiante

    # Renderizar el template y pasar la solicitud y los datos del estudiante al contexto
    return render(request, 'coordinador/ver_formulario.html', {
        'solicitud': solicitud,
        'estudiante': estudiante
    })

def correo_jefe_carrera(request, solicitud_id):
    # Recuperar la solicitud con el ID proporcionado
    solicitud = get_object_or_404(FichaInscripcion, id=solicitud_id)
    
    # Obtener el token de la URL
    token_str = request.GET.get('token')
    
    # Verificar que el token proporcionado sea válido (convertirlo a UUID)
    try:
        token = uuid.UUID(token_str)  # Convertir la cadena a un objeto UUID
    except ValueError:
        # Si no se puede convertir el token, significa que es inválido
        return render(request, "coordinador/correo_jefe_exito.html", {
            'solicitud': solicitud
        })
    
    # Validar si el token es válido
    if solicitud.token != token:
        return render(request, "coordinador/correo_jefe_exito.html", {
            'solicitud': solicitud
        })

    # Renderizar el formulario si el token es válido
    estudiante = solicitud.estudiante

    return render(request, 'coordinador/correo_jefe.html', {
        'solicitud': solicitud,
        'token': token_str,  # Usar el token original en la plantilla
        'estudiante': estudiante
    })

def correo_jefe_exito(request, solicitud_id):
    solicitud = get_object_or_404(FichaInscripcion, id=solicitud_id)

    return render(request, "coordinador/correo_jefe_exito.html", {
        'solicitud': solicitud
    })

def actualizar_estado(request, solicitud_id):
    solicitud = get_object_or_404(FichaInscripcion, id=solicitud_id)

    if request.method == 'POST':
        estado = request.POST.get('estado_solicitud')

        if estado in ['Jefe Carrera', 'Rechazada']:
            # Actualiza el estado de la solicitud
            solicitud.estado = estado
            solicitud.save()

            # Actualizar estado de la práctica relacionada
            practica = Practica.objects.get(fichainscripcion=solicitud)
            practica.estado = 'rechazada'
            practica.save()

            # Cuando el Coordinador apruebe una Solicitud, se enviará un correo al director
            if estado == 'Jefe Carrera':
                # Obtener el correo del director desde PracticaConfig
                try:
                    practica_config = PracticaConfig.objects.get()
                    correo_director = practica_config.correo_director
                except ObjectDoesNotExist:
                    correo_director = "fallback_director@example.com"  # Fallback en caso de no encontrar configuración

                # Generar token
                token = str(uuid.uuid4())
                solicitud.token = token
                solicitud.save()

                # Construir URL con token
                url_token = request.build_absolute_uri(
                    reverse('correo_jefe', kwargs={'solicitud_id': solicitud.id}) + f"?{urlencode({'token': token})}"
                )

                # Enviar el correo electrónico
                send_mail(
                    subject="Revisión de Práctica Profesional",
                    message=(
                        f"Estimado Jefe de Carrera:\n\n"
                        f"Se le ha asignado la revisión de una práctica profesional.\n\n"
                        f"Por favor, revise los detalles y tome una decisión: {url_token}\n\n"
                        f"Gracias."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[correo_director],  # Usar correo del director
                    fail_silently=False,
                )

        # Redirige a una página, como la lista de solicitudes
        return redirect('listar_practicas')

def actualizar_estado_jefe(request, solicitud_id):
    if request.method == 'POST':
        # Obtén la solicitud específica
        solicitud = get_object_or_404(FichaInscripcion, id=solicitud_id)

        # Verifica el valor de estado_solicitud desde el formulario
        estado = request.POST.get('estado_solicitud')

        if estado in ['Aprobada', 'Rechazada']:
            # Actualiza el estado de la solicitud
            solicitud.estado = estado
            solicitud.save()

            # Si el estado es "Aprobada", actualiza el estado de la práctica
            if estado == 'Aprobada':
                # Usa el nombre correcto del campo relacionado
                practica = Practica.objects.get(fichainscripcion=solicitud)
                practica.estado = 'en_progreso'  # Cambia el estado a "en_progreso"
                practica.save()

            # Si el estado es "Rechazada", actualiza el estado de la práctica
            if estado == 'Rechazada':
                # Usa el nombre correcto del campo relacionado
                practica = Practica.objects.get(fichainscripcion=solicitud)
                practica.estado = 'rechazada'  # Cambia el estado a "rechazada"
                practica.save()

            # Invalida el token eliminándolo o marcándolo como nulo
            solicitud.token = None
            solicitud.save()

        # Redirige a la página de éxito
        return redirect('correo_jefe_exito', solicitud_id=solicitud.id)
def configurar_correo_director(request):
    if request.method == 'POST':
        nuevo_correo = request.POST.get('correo_director')
        try:
            config = PracticaConfig.objects.get()
            config.correo_director = nuevo_correo
            config.save()
            messages.success(request, "El correo del director se ha actualizado correctamente.")
        except PracticaConfig.DoesNotExist:
            messages.error(request, "No se pudo encontrar la configuración para actualizar.")
        return redirect('documentos')

    # Renderizar la página si es necesario (para pruebas)
    return render(request, 'documentos.html')

def update_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return redirect('manage_documents')
    else:
        form = DocumentForm(instance=document)
    return render(request, 'documentos.html', {'form': form, 'documents': Document.objects.all()})

@coordinador_required
def documentos(request):
    # Tipos de documentos permitidos
    tipo_documentos = {
        'reglamento': 'Reglamento Práctica Profesional',
        'avance': 'Plantilla de informe',
    }

    # Obtener los documentos existentes por tipo
    documentos = []
    for tipo, descripcion in tipo_documentos.items():
        documento = Document.objects.filter(tipo=tipo).first()
        documentos.append({
            'tipo': tipo,
            'descripcion': descripcion,
            'documento': documento,
        })

    # Obtener la configuración o valores predeterminados
    configuracion = PracticaConfig.objects.first()
    if not configuracion:
        configuracion = PracticaConfig.objects.create()  # Crear configuración predeterminada si no existe

    fecha_inicio_limite = configuracion.fecha_inicio_limite
    fecha_termino_limite = configuracion.fecha_termino_limite
    correo_director = configuracion.correo_director

    # Formulario inicial vacío
    form = DocumentForm()

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Procesar documento
            tipo_documento = form.cleaned_data.get('tipo')
            archivo_nuevo = form.cleaned_data.get('archivo')

            documento = Document.objects.filter(tipo=tipo_documento).first()
            if documento:
                documento.archivo = archivo_nuevo
                documento.save()
            else:
                nuevo_documento = form.save(commit=False)
                nuevo_documento.tipo = tipo_documento
                nuevo_documento.save()

            messages.success(request, "Documento guardado correctamente.")
            return redirect('documentos')
        else:
            # Manejo simplificado de errores
            for error in form.errors.as_data().values():
                for e in error:
                    messages.error(request, e.message)

    # Pasar el contexto
    context = {
        'documentos': documentos,
        'form': form,
        'fecha_inicio_limite': fecha_inicio_limite,
        'fecha_termino_limite': fecha_termino_limite,
        'correo_director': correo_director,
    }

    return render(request, 'coordinador/documentos.html', context)


# Vista para ver documentos en el navegador (PDF y Word)
def ver_documento(request, document_id):
    documento = get_object_or_404(Document, id=document_id)
    file_path = documento.archivo.path

    # Si es un PDF, lo mostramos en línea
    if documento.archivo.name.endswith('.pdf'):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="{}"'.format(documento.archivo.name)
            return response

    # Si es un documento Word (.docx o .doc)
    elif documento.archivo.name.endswith('.docx') or documento.archivo.name.endswith('.doc'):
        file_url = documento.archivo.url  # URL pública del archivo
        return redirect(f"https://docs.google.com/viewer?url={file_url}&embedded=true")

    else:
        return HttpResponse("Formato no soportado", status=400)
    
def configurar_fechas(request):
    contexto = {}
    try:
        practica_config = PracticaConfig.objects.first()

        if not practica_config:
            practica_config = PracticaConfig.objects.create(
                fecha_inicio_limite="2024-01-01",
                fecha_termino_limite="2024-12-31"
            )

        if request.method == 'POST':
            fecha_inicio_limite = request.POST.get('fecha_inicio_limite', practica_config.fecha_inicio_limite)
            fecha_termino_limite = request.POST.get('fecha_termino_limite', practica_config.fecha_termino_limite)

            if fecha_inicio_limite > fecha_termino_limite:
                raise ValidationError("La fecha de inicio no puede ser mayor que la fecha de término.")

            practica_config.fecha_inicio_limite = fecha_inicio_limite
            practica_config.fecha_termino_limite = fecha_termino_limite
            practica_config.save()

            # Agrega un mensaje de éxito al contexto
            contexto['popup_success'] = "Las fechas de la práctica se han configurado correctamente."
            return render(request, 'coordinador/configurar_fechas.html', {'practica_config': practica_config, **contexto})

    except ValidationError as e:
        # Agrega un mensaje de error al contexto
        contexto['popup_error'] = str(e)

    except Exception:
        # Mensaje genérico en caso de errores inesperados
        contexto['popup_error'] = "Ocurrió un error inesperado. Intenta nuevamente más tarde."

    return render(request, 'coordinador/configurar_fechas.html', {'practica_config': practica_config, **contexto})



# Configuración de idioma para fechas en español
locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas

def generar_pdf_practica(request, ficha_id):
    try:
        ficha = FichaInscripcion.objects.get(pk=ficha_id)
    except FichaInscripcion.DoesNotExist:
        return HttpResponse("Ficha de inscripción no encontrada", status=404)

    estudiante = ficha.estudiante

    # Configurar la respuesta HTTP para el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="practica_{estudiante.usuario.username}.pdf"'

    # Crear el objeto Canvas
    buffer = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Fuentes y estilos
    encabezado_font = "Helvetica-Bold"
    cuerpo_font = "Helvetica"
    buffer.setFont(cuerpo_font, 12)

    # Espacios y márgenes
    margen_izquierdo = 50
    margen_derecho = 550
    margen_texto = 10  # Margen entre el logo y el texto

    # Encabezado: Logo arriba a la izquierda con escala
    logo_path = 'autenticacion/static/img/universidad_logo.png'
    try:
        logo = ImageReader(logo_path)
        original_width, original_height = logo.getSize()
        max_logo_height = 45
        scale_factor = max_logo_height / original_height
        scaled_width = original_width * scale_factor
        scaled_height = original_height * scale_factor
        buffer.drawImage(
            logo, margen_izquierdo, height - scaled_height - 30,
            width=scaled_width, height=scaled_height, mask='auto'
        )
    except Exception as e:
        print(f"Error cargando el logo: {e}")

    # Ajustar el texto para que esté a la derecha del logo
    text_x_position = margen_izquierdo + scaled_width + margen_texto

    # Título centrado
    buffer.setFont(encabezado_font, 14)
    buffer.drawString(text_x_position, height - 50, "UNIVERSIDAD AUTÓNOMA DE CHILE")

    # Subtítulo
    buffer.setFont(cuerpo_font, 12)
    buffer.drawString(text_x_position, height - 70, "Facultad de Ingeniería - Sede Santiago")

    # Fecha a la derecha
    buffer.drawRightString(margen_derecho, height - 140, f"Santiago, {datetime.now().strftime('%d de %B del %Y')}")

    # Saludo
    buffer.setFont(cuerpo_font, 12)
    buffer.drawString(margen_izquierdo, height - 200, "Señores:")

    # Datos en negrita
    buffer.setFont(encabezado_font, 12)
    buffer.drawString(margen_izquierdo, height - 220, f"{ficha.razon_social}")
    buffer.setFont(cuerpo_font, 12)
    buffer.drawString(margen_izquierdo, height - 240, "Presente")

    # Cuerpo del texto con datos en negrita
    texto = f"""
    De nuestra consideración:

    UNIVERSIDAD AUTÓNOMA DE CHILE informa a usted que <b>{estudiante.usuario.first_name} {estudiante.usuario.last_name}</b>, 
    RUN <b>{estudiante.rut}</b>, es alumno regular de la carrera de <b>{estudiante.carrera}</b> de la Facultad de Ingeniería.

    De conformidad con el plan de estudios, debe realizar su Práctica Profesional, la cual comenzará el día 
    <b>{ficha.fecha_inicio.strftime('%d de %B del %Y')}</b> y finalizará el <b>{ficha.fecha_termino.strftime('%d de %B del %Y')}</b>, ambas fechas inclusive. 

    Tanto el periodo como las funciones realizadas por el alumno en práctica serán 
    inspeccionadas constantemente por el Coordinador de Prácticas de la carrera de 
    Ingeniería Civil Informática.

    Se hace mención que, durante el periodo de práctica antes indicado, el alumno se 
    encuentra protegido por la Ley 16.744, sobre Accidentes del Trabajo y Enfermedades 
    Profesionales.
    """
    
    # Estilos para el texto justificado
    style = ParagraphStyle(
        name='Normal', 
        fontName='Helvetica', 
        fontSize=12, 
        spaceAfter=6,
        alignment=4,  # Justificado
        leftIndent=20,  # Margen izquierdo
        rightIndent=20,  # Margen derecho
        wordSpace=1.0,
        lineHeight=14,
    )

    # Crear el párrafo con el texto a insertar
    paragraph = Paragraph(texto, style)

    # Dibujar el párrafo en el canvas en la posición deseada
    paragraph_width, paragraph_height = paragraph.wrap(width - 100, height)  # Ajuste de márgenes
    paragraph.drawOn(buffer, margen_izquierdo, height - 300 - paragraph_height)

    # Timbre al final de la página (centrado)
    timbre_path = 'autenticacion/static/img/timbre.png'
    try:
        timbre = ImageReader(timbre_path)
        timbre_width, timbre_height = timbre.getSize()
        max_timbre_height = 250
        timbre_scale_factor = max_timbre_height / timbre_height
        scaled_timbre_width = timbre_width * timbre_scale_factor
        scaled_timbre_height = timbre_height * timbre_scale_factor
        timbre_x = (width - scaled_timbre_width) / 2
        timbre_y = 50
        buffer.drawImage(timbre, timbre_x, timbre_y, width=scaled_timbre_width, height=scaled_timbre_height, mask='auto')
    except Exception as e:
        print(f"Error cargando el timbre: {e}")

    # Finalizar el PDF
    buffer.showPage()
    buffer.save()
    return response

def enviar_formulario(request, ficha_id):
    ficha = get_object_or_404(FichaInscripcion, id=ficha_id)
    
    # Crear o recuperar el token único
    token, created = FormularioToken.objects.get_or_create(ficha_inscripcion=ficha)
    
    # Construir el enlace único con dominio válido
    base_url = "http://localhost:8000"  # Cambia esto por tu dominio real para producción
    enlace = f"{base_url}/coordinador/formulario/{token.token}/"
    
    # Enviar el correo al supervisor
    subject = "Formulario de Evaluación de Práctica Profesional"
    message = f"""
    Estimado {ficha.jefe_directo},

    Por favor, complete el formulario de evaluación de la práctica profesional del estudiante {ficha.estudiante.usuario.first_name} {ficha.estudiante.usuario.last_name}.
    Puede acceder al formulario mediante el siguiente enlace:

    {enlace}

    Muchas gracias,
    Equipo de Coordinación
    """
    recipient = ficha.correo_jefe
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])
    
    # Marcar como enviado
    token.enviado = True
    token.save()


def completar_formulario(request, token):
    """
    Maneja la visualización y envío del formulario confidencial asociado a una ficha.
    
    Args:
        request: Objeto de solicitud HTTP.
        token: Token único asociado al formulario.
    
    Returns:
        Renderiza la plantilla 'coordinador/completar_formulario.html'.
    """
    # Obtener el token y la ficha asociada
    formulario_token = get_object_or_404(FormularioToken, token=token)
    ficha = formulario_token.ficha_inscripcion

    # Control para mostrar el modal de éxito en la plantilla
    form_success = False

    if request.method == 'POST':
        # Crear una instancia del formulario con los datos enviados
        form = InformeConfidencialForm(request.POST, ficha_inscripcion=ficha)
        if form.is_valid():
            # Crear la instancia pero no guardarla aún en la base de datos
            informe_confidencial = form.save(commit=False)

            # Calcular la nota antes de guardar el informe
            informe_confidencial.calcular_nota()

            # Guardar el informe con la nota calculada
            informe_confidencial.save()

            # Marcar el formulario como exitosamente completado
            form_success = True
        else:
            # Mostrar los errores en la consola para facilitar la depuración
            print("Errores del formulario:", form.errors)
    else:
        # Si la solicitud es GET, renderizar el formulario vacío
        form = InformeConfidencialForm(ficha_inscripcion=ficha)

    # Renderizar la plantilla con el formulario y el estado de éxito
    return render(
        request,
        'coordinador/completar_formulario.html',
        {
            'form': form,
            'ficha': ficha,
            'form_success': form_success,  # Indica si se debe mostrar el modal
        }
    )


def listado_informes_confidenciales(request):
    # Obtener todos los informes confidenciales
    informes = InformeConfidencial.objects.all()

    return render(request, 'coordinador/listado_informes_confidenciales.html', {'informes': informes})

def editar_informe_confidencial(request, informe_id):
    # Obtener el informe correspondiente
    informe = get_object_or_404(InformeConfidencial, id=informe_id)

    if request.method == 'POST':
        # Obtener la nota manual desde el formulario (si se envía)
        nota_manual = request.POST.get('nota_manual')
        
        # Si se ha proporcionado una nota manual, intentamos actualizarla
        if nota_manual:
            try:
                informe.nota = float(nota_manual)  # Convertimos la nota a flotante
                informe.save()  # Guardamos el cambio directamente en el registro
                messages.success(request, 'Nota actualizada con éxito.')
            except ValueError:
                # Si no se puede convertir la nota a un número flotante, agregamos un error
                messages.error(request, 'La nota manual debe ser un número válido.')
        
        return redirect('listado_informes_confidenciales')  # Redirigir al listado de informes

    # Si el método es GET, simplemente mostramos la vista para editar
    return render(request, 'coordinador/editar_informe_confidencial.html', {'informe': informe})

@coordinador_required
def descargar_informe(request, practica_id):
    practica = Practica.objects.get(pk=practica_id)
    informe = practica.informeavances_set.last()
    if informe and informe.archivo_informe_avances:
        return FileResponse(informe.archivo_informe_avances)
    else:
        return HttpResponseNotFound("Informe no encontrado")
    
    from django.utils import timezone

def crear_notificacion(usuario, mensaje, tipo='info'):
    notificacion = Notificacion.objects.create(
        usuario=usuario,
        mensaje=mensaje,
        tipo=tipo,
        fecha_creacion=timezone.now()
    )
    notificacion.save()

from django.shortcuts import render, get_object_or_404, redirect
from .models import Practica, FichaInscripcion, Autoevaluacion, InformeAvances, InformeFinal, InformeConfidencial

def detalle_practica_coordinador(request, practica_id):
    practica = get_object_or_404(Practica, id=practica_id)
    ficha_inscripcion = FichaInscripcion.objects.filter(practica=practica).first()
    autoevaluacion = Autoevaluacion.objects.filter(practica=practica).first()

    if request.method == "POST":
        if "archivo_informe_avances" in request.FILES:
            archivo = request.FILES.get("archivo_informe_avances")
            informe_avances, created = InformeAvances.objects.get_or_create(practica=practica)
            if informe_avances.archivo_informe_avances:
                informe_avances.archivo_informe_avances.delete()  # Eliminar archivo anterior
            informe_avances.archivo_informe_avances = archivo
            informe_avances.intentos_subida += 1
            informe_avances.save()

        if "archivo_informe_final" in request.FILES:
            archivo_final = request.FILES.get("archivo_informe_final")
            informe_final, created = InformeFinal.objects.get_or_create(practica=practica)
            if informe_final.archivo_informe_final:
                informe_final.archivo_informe_final.delete()  # Eliminar archivo anterior
            informe_final.archivo_informe_final = archivo_final
            informe_final.intentos_subida_final += 1
            informe_final.save()

        return redirect('detalle_practica_coordinador', practica_id=practica.id)

    informe_avances = InformeAvances.objects.filter(practica=practica).first()
    informe_final = InformeFinal.objects.filter(practica=practica).first()
    informe_confidencial = InformeConfidencial.objects.filter(practica=practica).first()

    nota_autoevaluacion = autoevaluacion.nota if autoevaluacion else None
    informe_avances_enviado = InformeAvances.objects.filter(practica=practica).exists()

    return render(request, 'coordinador/detalle_practica.html', {
        'practica': practica,
        'ficha_inscripcion': ficha_inscripcion,
        'estado_ficha': ficha_inscripcion.estado if ficha_inscripcion else None,
        'nota_autoevaluacion': nota_autoevaluacion,
        'autoevaluacion': autoevaluacion,
        'informe_avances_enviado': informe_avances_enviado,
        'informe_confidencial': informe_confidencial,
    })

@coordinador_required
def evaluar_informe(request, practica_id):
    practica = get_object_or_404(Practica, pk=practica_id)
    informe = practica.informeavances_set.last()  # Obtener el último informe de avances

    # Obtener estudiante relacionado con la práctica
    estudiante = practica.estudiante

    # Obtener la FichaInscripcion asociada con la práctica
    ficha_inscripcion = FichaInscripcion.objects.filter(practica=practica).first()

    coordinador = request.user

    # Contexto para la plantilla
    context = {
        "practica": practica,
        "informe": informe,
        "estudiante": estudiante,
        "ficha_inscripcion": ficha_inscripcion,  # Pasar la ficha de inscripción
        "coordinador": coordinador,  # Pasar datos del coordinador
}

    if request.method == "POST":
        # Obtener criterios desde el formulario
        criterios = [
            request.POST.get("portada"),
            request.POST.get("introduccion"),
            request.POST.get("objetivo_general"),
            request.POST.get("objetivos_especificos"),
            request.POST.get("caracterizacion_empresa"),
            request.POST.get("datos_supervisor"),
            request.POST.get("desarrollo_practica"),
            request.POST.get("formato_establecido"),
        ]

        # Asignar puntajes según el criterio
        puntajes = {
            "Desempeño de excelencia": 4,
            "Desempeño efectivo": 3,
            "Desempeño que se debe mejorar": 2,
            "Desempeño insatisfactorio": 1,
        }

        # Calcular el total de puntajes obtenidos
        total_puntaje_obtenido = sum(puntajes.get(criterio, 0) for criterio in criterios if criterio)

        # Determinar el puntaje máximo y mínimo posibles
        max_puntaje = len(criterios) * 4  # Todos con "Desempeño de excelencia"
        min_puntaje = len(criterios) * 1  # Todos con "Desempeño insatisfactorio"

        if max_puntaje > min_puntaje:
            # Escalar la nota final al rango de 1.0 a 7.0
            nota_final = 1.0 + ((total_puntaje_obtenido - min_puntaje) * 6.0 / (max_puntaje - min_puntaje))
        else:
            nota_final = 1.0

        nota_final = round(nota_final, 1)  # Redondear a un decimal

        if informe:
            informe.nota_avance = nota_final
            informe.retroalimentacion = request.POST.get("comentarios", "")
            informe.save()
            messages.success(request, f"El informe ha sido evaluado exitosamente. Nota: {nota_final}")
            return redirect('informes_avances')
        else:
            messages.error(request, "No se encontró un informe asociado a esta práctica.")

    return render(request, 'coordinador/evaluar_informe.html', context)
