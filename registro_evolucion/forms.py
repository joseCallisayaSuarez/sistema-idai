# registro_evolucion/forms.py
from django import forms
from .models import InformeFinal, DesarrolloEducativo, AreaDesarrollo

# registro_evolucion/forms.py
class InformeFinalForm(forms.ModelForm):
    class Meta:
        model = InformeFinal
        fields = [
            'estudiante',
            'diagnostico_educativo', 
            'semestre_programa',
            'gestion',
            'otras_senales_alerta',
            'estado_final',
            'director',
            'sello_direccion',
            'lugar_fecha'
        ]
        widgets = {
            'estudiante': forms.HiddenInput(),  # Hacerlo oculto
            'diagnostico_educativo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'otras_senales_alerta': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'estado_final': forms.TextInput(attrs={'class': 'form-control'}),
            'director': forms.TextInput(attrs={'class': 'form-control'}),
            'lugar_fecha': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: La Paz, noviembre de 2025'}),
            'semestre_programa': forms.Select(attrs={'class': 'form-control'}),
            'gestion': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer el campo estudiante no requerido en el frontend (se valida en el backend)
        self.fields['estudiante'].required = False
class DesarrolloEducativoForm(forms.ModelForm):
    class Meta:
        model = DesarrolloEducativo
        fields = ['area', 'evaluacion', 'recomendaciones']
        widgets = {
            'area': forms.HiddenInput(),
            'evaluacion': forms.Select(attrs={'class': 'form-control'}),
            'recomendaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

# Formset para múltiples desarrollos educativos
DesarrolloEducativoFormSet = forms.inlineformset_factory(
    InformeFinal,
    DesarrolloEducativo,
    form=DesarrolloEducativoForm,
    extra=0,
    can_delete=False,
    min_num=1,
    validate_min=True
)