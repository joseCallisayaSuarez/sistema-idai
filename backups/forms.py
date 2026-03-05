from django import forms
from .models import Backup

class BackupForm(forms.ModelForm):
    class Meta:
        model = Backup
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md',
                'placeholder': 'Ej: Backup completo diciembre 2024'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-md',
                'rows': 3,
                'placeholder': 'Descripción del backup (opcional)'
            }),
        }

class RestoreForm(forms.Form):
    backup = forms.ModelChoiceField(
        queryset=Backup.objects.filter(estado='completado'),
        required=False,
        label='Seleccionar backup existente',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border rounded-md'
        })
    )
    
    archivo = forms.FileField(
        required=False,
        label='O subir archivo de backup',
        widget=forms.FileInput(attrs={
            'class': 'w-full px-3 py-2 border rounded-md',
            'accept': '.json'
        })
    )
    
    confirmar = forms.BooleanField(
        required=False,
        label='Confirmo que quiero restaurar el sistema',
        widget=forms.CheckboxInput(attrs={
            'class': 'mr-2'
        })
    )