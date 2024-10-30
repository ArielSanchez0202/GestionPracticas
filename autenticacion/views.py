from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import SendMailForm, SetPasswordForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.views import View
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
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
                    return redirect('coordinador:listar_estudiantes')  # Cambia esto por la URL del coordinador
                elif user.groups.filter(name='Estudiante').exists():
                    return redirect('estudiante:estudiantes_main')  # Cambia esto por la URL del estudiante
                else:
                    return redirect('home')  # URL predeterminada

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
            # Lógica para enviar el correo
            # ...
            return render(request, 'password_reset_done.html')
        return render(request, 'password_reset_form.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')