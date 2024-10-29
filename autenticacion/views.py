from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
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

# Create your views here.
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

#Login Vacío, BORRAR AL IMPLEMENTAR
def login_view(request):
    return render(request, 'login.html')