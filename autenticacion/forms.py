from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm

class SendMailForm(forms.Form):
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ingresa tu correo electrónico',
            'class': 'input-password_reset'  # Aquí puedes añadir clases CSS
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')  # Obtener el correo del formulario
        # Verificar si existe un usuario con el correo ingresado
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No existe ningún usuario con este correo.")
        return email

class PasswordResetForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'Nueva contraseña'}),
        label='',  # Eliminar el label ya que se reemplaza por el placeholder
        help_text='Ingrese una nueva contraseña',
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'Confirmar contraseña'}),
        label='',  # Eliminar el label ya que se reemplaza por el placeholder
        help_text='Repita la nueva contraseña',
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user  # Guardar el usuario para la validación
        super().__init__(*args, **kwargs)

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')

        # Comprobar que la nueva contraseña no sea igual a la contraseña actual
        if self.user.check_password(password1):
            raise ValidationError("La nueva contraseña no puede ser la misma que la contraseña actual.")

        return password1

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return password2
    
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')

        # Validación del formato
        if not re.match(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$', rut):
            raise forms.ValidationError('El RUT debe estar en el formato XX.XXX.XXX-X.')

        # Se remueve el punto y el guión
        clean_rut = rut.replace(".", "").replace("-", "")

        # Se extrae la parte numérica y se verifica el dígito
        num_part = clean_rut[:-1]
        dv = clean_rut[-1].upper()

        # Validación del dígito verificador
        reversed_digits = map(int, reversed(num_part))
        factors = cycle(range(2, 8))
        s = sum(d * f for d, f in zip(reversed_digits, factors))
        verificador = (-s) % 11
        verificador = 'K' if verificador == 10 else str(verificador)

        # Validación del dígito verificador
        if dv != verificador:
            raise forms.ValidationError('El dígito verificador del RUT no es válido.')
        return rut