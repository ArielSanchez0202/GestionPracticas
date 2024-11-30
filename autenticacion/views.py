from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from autenticacion.decorators import coordinador_required
from .forms import PasswordResetForm
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib import messages
from .models import User
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.models import User

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                messages.error(request, "Tu cuenta ha sido bloqueada. Comuníquese con un administrador.", extra_tags='login_error')
                return render(request, 'login.html')

            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Has iniciado sesión con éxito.")
                
                # Verifica si es el primer inicio de sesión
                if hasattr(user, 'coordinador') and user.coordinador.first_login:
                    return redirect('change_password')
                elif hasattr(user, 'estudiante') and user.estudiante.first_login:
                    return redirect('change_password')

                # Redirección según el rol después del cambio de contraseña
                if user.groups.filter(name='Coordinador').exists():
                    return redirect('listar_estudiantes')
                elif user.groups.filter(name='Estudiante').exists():
                    return redirect('estudiantes_main')
            else:
                messages.error(request, "Correo o contraseña incorrectos.", extra_tags='login_error')
                
        except User.DoesNotExist:
            messages.error(request, "No existe un usuario activo con ese correo electrónico.", extra_tags='login_error')

    return render(request, 'login.html')


#vista para cambiar contraseña cuando se inicia sesion por primera vez
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()

            # Desactiva `first_login` si es el primer inicio de sesión
            if hasattr(user, 'coordinador'):
                user.coordinador.first_login = False
                user.coordinador.save()
            elif hasattr(user, 'estudiante'):
                user.estudiante.first_login = False
                user.estudiante.save()

            update_session_auth_hash(request, user)  # Mantiene la sesión activa
            messages.success(request, 'Contraseña cambiada exitosamente.')
            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'password_change_form.html', {'form': form})

# Vista para solicitar el restablecimiento de contraseña
def custom_password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse('custom_password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            # Enviar el correo
            subject = "Restablecimiento de contraseña"
            message = render_to_string("password_reset_email.html", {
                'user': user,
                'protocol': 'https' if request.is_secure() else 'http',
                'domain': request.get_host(),
                'uidb64': uid,  # uid codificado
                'token': token,  # token generado
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
            return redirect("custom_password_reset_done")
        except User.DoesNotExist:
            messages.error(request, "No se encontró una cuenta con ese correo.", extra_tags='reset_error')
    return render(request, "password_reset_form.html")

# Vista para mostrar mensaje de éxito al enviar el correo
def custom_password_reset_done(request):
    return render(request, "password_reset_done.html")

# Vista para confirmar el token y permitir al usuario cambiar la contraseña
def custom_password_reset_confirm(request, uidb64, token):
    try:
        # Decodificar el UID y obtener el usuario
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Verificar que el token sea válido para el usuario
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = PasswordResetForm(user, request.POST)
            if form.is_valid():
                # Establecer la nueva contraseña
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                messages.success(request, "Su contraseña ha sido restablecida exitosamente.")
                return redirect("custom_password_reset_complete")
        else:
            form = PasswordResetForm(user)
    else:
        messages.error(request, "El enlace de restablecimiento de contraseña no es válido o ha expirado.")
        return redirect("custom_password_reset")

    return render(request, "password_reset_confirm.html", {"form": form})

# Vista para confirmar que el restablecimiento de contraseña fue exitoso
def custom_password_reset_complete(request):
    return render(request, "password_reset_complete.html")

def user_logout(request):
    logout(request)
    return redirect('home')

@coordinador_required
def bloquear_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_active:
        user.is_active = False
        user.save()
        messages.success(request, f"El usuario {user.username} ha sido bloqueado.")
    else:
        messages.info(request, f"El usuario {user.username} ya está bloqueado.")
    return redirect('listar_estudiantes')

@coordinador_required
def desbloquear_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not user.is_active:
        user.is_active = True
        user.save()
        messages.success(request, f"El usuario {user.username} ha sido desbloqueado.")
    else:
        messages.info(request, f"El usuario {user.username} ya está desbloqueado.")
    return redirect('listar_estudiantes')
