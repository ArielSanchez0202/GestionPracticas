from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import SendMailForm, SetPasswordForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import PasswordResetConfirmView, LogoutView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.views import View
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib import messages
from .models import User 

# Create your views here.
def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Has iniciado sesión con éxito.")
                
                # Redirección basada en el grupo del usuario
                if user.groups.filter(name='Coordinador').exists():
                    return redirect('coordinador:listar_coordinador')  # Cambia esto por la URL del coordinador
                elif user.groups.filter(name='Estudiante').exists():
                    return redirect('estudiante:estudiantes_main')  # Cambia esto por la URL del estudiante
            else:
                messages.error(request, "Nombre de usuario o contraseña incorrectos.")
        except User.DoesNotExist:
            messages.error(request, "No existe un usuario con ese correo electrónico.")
    
    return render(request, 'login.html')  # Asegúrate de que este template esté en la carpeta correcta

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = SetPasswordForm
    success_url = reverse_lazy('password_reset_complete')

class SendMailConfirmView(View):
    def get(self, request):
        form = SendMailForm()
        return render(request, 'password_reset_form.html', {'form': form})

    def post(self, request):
        form = SendMailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            # Generar el token de restablecimiento de contraseña
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Enviar el correo electrónico con el enlace de restablecimiento
            password_reset_url = request.build_absolute_uri(
                reverse_lazy('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            send_mail(
                subject='Restablecimiento de contraseña',
                message=f'Usa el siguiente enlace para restablecer tu contraseña: {password_reset_url}',
                from_email='tu_email@dominio.com',
                recipient_list=[email],
            )

            # Redirigir a la página de confirmación si el correo fue enviado exitosamente
            return redirect('password_reset_done')

        # Mostrar el error en la misma página si el correo no es válido
        return render(request, 'password_reset_form.html', {'form': form})
    
def user_logout(request):
    logout(request)  # Cierra la sesión del usuario
    return redirect('home')

@login_required
def bloquear_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if  user.is_active:
        user.is_active = False
        user.save()
        messages.success(request, f"El usuario {user.username} ha sido bloqueado.")
    else:
        messages.info(request, f"El usuario {user.username} ya está bloqueado.")
    return redirect('coordinador:listar_estudiantes')

@login_required
def desbloquear_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not user.is_active:
        user.is_active = True
        user.save()
        messages.success(request, f"El usuario {user.username} ha sido desbloqueado.")
    else:
        messages.info(request, f"El usuario {user.username} ya está desbloqueado.")
    return redirect('coordinador:listar_estudiantes')