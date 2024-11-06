from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from autenticacion.decorators import coordinador_required
from .forms import SendMailForm, SetPasswordForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.views import View
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from .models import User
from django.contrib.auth.models import User

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                messages.error(request, "Tu cuenta ha sido bloqueada. Comuníquese con un administrador.")
                return render(request, 'login.html')

            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Has iniciado sesión con éxito.")

                if user.groups.filter(name='Coordinador').exists():
                    return redirect('coordinador:listar_estudiantes')
                elif user.groups.filter(name='Estudiante').exists():
                    return redirect('estudiante:estudiantes_main')
            else:
                messages.error(request, "Nombre de usuario o contraseña incorrectos.")
                
        except User.DoesNotExist:
            messages.error(request, "No existe un usuario activo con ese correo electrónico.")

    return render(request, 'login.html')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = SetPasswordForm
    success_url = reverse_lazy('password_reset_complete')

class SendMailConfirmView(View):
    def get(self, request):
        form = SendMailForm()
        return render(request, 'autenticacion/password_reset_form.html', {'form': form})

    def post(self, request):
        form = SendMailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                password_reset_url = request.build_absolute_uri(
                    reverse('autenticacion:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                send_mail(
                    subject='Restablecimiento de contraseña',
                    message=f'Usa el siguiente enlace para restablecer tu contraseña: {password_reset_url}',
                    from_email='tu_email@dominio.com',
                    recipient_list=[email],
                )

                return redirect('autenticacion:password_reset_done')
            except User.DoesNotExist:
                messages.error(request, "No existe un usuario registrado con ese correo electrónico.")
                return render(request, 'autenticacion/password_reset_form.html', {'form': form})

        return render(request, 'autenticacion/password_reset_form.html', {'form': form})

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
    return redirect('coordinador:listar_estudiantes')

@coordinador_required
def desbloquear_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not user.is_active:
        user.is_active = True
        user.save()
        messages.success(request, f"El usuario {user.username} ha sido desbloqueado.")
    else:
        messages.info(request, f"El usuario {user.username} ya está desbloqueado.")
    return redirect('coordinador:listar_estudiantes')
