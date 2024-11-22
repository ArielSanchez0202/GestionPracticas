
from django import forms
from .models import Document, PracticaConfig


# Validador personalizado para solo permitir PDF y archivos Word (.doc, .docx)
def validate_file_type(value):
    # Definimos las extensiones permitidas (incluyendo .doc y .docx)
    valid_extensions = ['.pdf', '.doc', '.docx']
    # Comprobamos si la extensión del archivo es válida
    if not any(value.name.endswith(ext) for ext in valid_extensions):
        raise forms.ValidationError("Solo se permiten archivos PDF y Word (.doc, .docx)")

class DocumentForm(forms.ModelForm):
    archivo = forms.FileField(validators=[validate_file_type])  # Aplicamos el validador

    class Meta:
        model = Document
        fields = ['archivo']
class PracticaConfigForm(forms.ModelForm):
    class Meta:
        model = PracticaConfig
        fields = ['fecha_inicio_limite', 'fecha_termino_limite']
        widgets = {
            'fecha_inicio_limite': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_termino_limite': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }