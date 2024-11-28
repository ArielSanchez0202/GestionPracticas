
from django import forms
from .models import Document, InformeConfidencial, PracticaConfig


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
class InformeConfidencialForm(forms.ModelForm):
    class Meta:
        model = InformeConfidencial
        fields = '__all__'  # Incluye todos los campos del modelo
        exclude = ['nota']  # Excluir el campo que se calcula automáticamente
        widgets = {
            # Campos relacionados con observaciones (TextAreas)
            'calidad_observacion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'efectividad_observacion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'conocimientos_observacion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'adaptabilidad_observacion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'organizacion_observacion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'interes_observacion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'responsabilidad_observacion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'cooperacion_observacion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'creatividad_observacion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'iniciativa_observacion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'integracion_observacion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'tipo_especialidad': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),

            # Campos de selección (Dropdowns)
            'calidad_trabajo': forms.Select(attrs={'class': 'form-select'}),
            'efectividad_trabajo': forms.Select(attrs={'class': 'form-select'}),
            'conocimientos_profesionales': forms.Select(attrs={'class': 'form-select'}),
            'adaptabilidad_cambios': forms.Select(attrs={'class': 'form-select'}),
            'organizacion_trabajo': forms.Select(attrs={'class': 'form-select'}),
            'interes_trabajo': forms.Select(attrs={'class': 'form-select'}),
            'responsabilidad': forms.Select(attrs={'class': 'form-select'}),
            'cooperacion_trabajo': forms.Select(attrs={'class': 'form-select'}),
            'creatividad': forms.Select(attrs={'class': 'form-select'}),
            'iniciativa': forms.Select(attrs={'class': 'form-select'}),
            'integracion_grupo': forms.Select(attrs={'class': 'form-select'}),

            # Pregunta adicional (Checkbox)
            'positivo_recibir': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        ficha_inscripcion = kwargs.pop('ficha_inscripcion', None)
        super().__init__(*args, **kwargs)

        # Si ficha_inscripcion es proporcionado, lo pre-rellenamos y lo hacemos oculto
        if ficha_inscripcion:
            self.fields['ficha_inscripcion'].initial = ficha_inscripcion
            self.fields['ficha_inscripcion'].widget = forms.HiddenInput()  # Lo ocultamos en el formulario
