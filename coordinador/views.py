import locale
import re
import secrets
import string
from datetime import datetime
from smtplib import SMTPException
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.messages import get_messages
from django.core.mail import send_mail
from django.http import BadHeaderError, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import json
import logging
from django.shortcuts import get_object_or_404, render, redirect
from autenticacion.decorators import coordinador_required
from .forms import DocumentForm
from .models import Coordinador, Document, Estudiante, PracticaConfig, FichaInscripcion, Autoevaluacion, Practica
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader

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
def informes_avances(request):
    return render(request, 'coordinador/informes_avances.html')

@coordinador_required
def autoevaluaciones(request):
    # Obtener los RUT de los estudiantes activos
    estudiantes_activos = Estudiante.objects.filter(usuario__is_active=True).values_list('rut', flat=True)
    
    # Filtrar inscripciones solo para estudiantes con esos RUT
    inscripciones = FichaInscripcion.objects.filter(estudiante__rut__in=estudiantes_activos)
    
    # Obtener las autoevaluaciones relacionadas con las prácticas
    autoevaluaciones = Autoevaluacion.objects.all()  # Asumimos que existe una relación entre 'Autoevaluacion' y 'FichaInscripcion'
    
    return render(request, 'coordinador/autoevaluaciones.html', {
        'inscripciones': inscripciones,
        'autoevaluaciones': autoevaluaciones,
    })

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

@csrf_protect
@require_POST
def guardar_nota(request, autoevaluacion_id):
    try:
        # Parsear los datos JSON de la solicitud
        data = json.loads(request.body)
        nota = data.get('nota')

        # Validar que la nota sea un número decimal válido
        try:
            nota = float(nota)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Nota inválida'}, status=400)

        # Buscar la autoevaluación o devolver 404
        autoevaluacion = get_object_or_404(Autoevaluacion, id=autoevaluacion_id)
        
        # Guardar la nueva nota
        autoevaluacion.nota = nota
        autoevaluacion.save()
        
        return JsonResponse({'nota': str(nota)})
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

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

def actualizar_estado(request, solicitud_id):
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
                try:
                    # Usa el nombre correcto del campo relacionado
                    practica = Practica.objects.get(fichainscripcion=solicitud)
                    practica.estado = 'en_progreso'  # Cambia el estado a "en_progreso"
                    practica.save()
                except Practica.DoesNotExist:
                    # Manejo de error en caso de que no exista una práctica asociada
                    messages.error(request, "No se encontró una práctica asociada a esta solicitud.")

        # Redirige a una página, como la lista de solicitudes o el detalle de la solicitud
        return redirect('listar_practicas')  # Cambia a la vista adecuada
    

def manage_documents_view(request):
    documents = Document.objects.all()
    return render(request, 'documentos.html', {'documents': documents})

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
        'ficha_inscripcion': 'Ficha de inscripción práctica profesional',
        'informe_avances': 'Informe de avances',
        'autoevaluacion': 'Autoevaluación',
    }

    # Obtener los documentos existentes por tipo
    documentos = []
    for tipo, descripcion in tipo_documentos.items():
        documento = Document.objects.filter(tipo=tipo).first()
        documentos.append({
            'tipo': tipo,
            'descripcion': descripcion,
            'documento': documento
        })

    # Formulario inicial vacío
    form = DocumentForm()

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Determinar el tipo de documento
            tipo_documento = form.cleaned_data.get('tipo')
            archivo_nuevo = form.cleaned_data.get('archivo')

            # Buscar documento existente por tipo
            documento = Document.objects.filter(tipo=tipo_documento).first()

            if documento:
                # Si existe, sobrescribir archivo
                documento.archivo = archivo_nuevo
                documento.save()
            else:
                # Si no existe, crear uno nuevo
                nuevo_documento = form.save(commit=False)
                nuevo_documento.tipo = tipo_documento
                nuevo_documento.save()

            # Redirigir tras guardar
            return redirect('documentos')

        else:
            # Mostrar errores en los mensajes
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")

    return render(request, 'coordinador/documentos.html', {'documentos': documentos, 'form': form})

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
    # Obtener la configuración de fechas de la práctica, o crear una nueva si no existe
    practica_config = PracticaConfig.objects.first()

    # Si no existe una configuración de práctica, crear una nueva
    if not practica_config:
        practica_config = PracticaConfig.objects.create(
            fecha_inicio_limite="2024-01-01",  # O las fechas predeterminadas que desees
            fecha_termino_limite="2024-12-31"
        )

    if request.method == 'POST':
        # Guardar las nuevas fechas (asegurarse de que los datos sean válidos)
        practica_config.fecha_inicio_limite = request.POST.get('fecha_inicio_limite', practica_config.fecha_inicio_limite)
        practica_config.fecha_termino_limite = request.POST.get('fecha_termino_limite', practica_config.fecha_termino_limite)
        practica_config.save()
        # Redirigir a la página de documentos u otra página de tu elección
        return redirect('documentos')

    return render(request, 'coordinador/configurar_fechas.html', {
        'practica_config': practica_config
    })




# Configuración de idioma para fechas en español
locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

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
