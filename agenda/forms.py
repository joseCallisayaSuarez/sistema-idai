from django import forms
from .models import AgendaEstudiante, Sesion
from estudiantes.models import Estudiante

class BuscarEstudianteForm(forms.Form):
    ci_estudiante = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Ingrese CI del estudiante...'
        }),
        label="Cédula de Identidad"
    )

class AgendaForm(forms.ModelForm):
    class Meta:
        model = AgendaEstudiante
        fields = ['dia_semana', 'hora_inicio', 'hora_fin', 'fecha_inicio']
        widgets = {
            'dia_semana': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'type': 'time', 
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'type': 'time', 
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
        }

class SesionForm(forms.ModelForm):
    estado = forms.ChoiceField(
        choices=[
            ('programada', '🟡 Programada'),
            ('asistio', '🟢 Asistió'),
            ('ausente', '🔴 Ausente'),
            ('justificada', '🟠 Justificada'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        })
    )
    
    class Meta:
        model = Sesion
        fields = ['estado', 'progreso', 'observaciones', 'justificacion']
        widgets = {
            'progreso': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '1-10',
                'min': '1',
                'max': '10'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Observaciones del desempeño del estudiante en la sesión...',
            }),
            'justificacion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Motivo de la justificación...',
            }),
        }

class AsistenciaForm(forms.ModelForm):
    estado = forms.ChoiceField(
        choices=[
            ('programada', '🟡 Programada'),
            ('asistio', '🟢 Asistió'),
            ('ausente', '🔴 Ausente'),
            ('justificada', '🟠 Justificada'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'id': 'id_estado'
        })
    )
    
    class Meta:
        model = Sesion
        fields = ['estado', 'progreso', 'observaciones', 'justificacion']
        widgets = {
            'progreso': forms.NumberInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': '1-10',
                'min': '1',
                'max': '10',
                'id': 'id_progreso'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Observaciones del desempeño del estudiante...',
                'id': 'id_observaciones'
            }),
            'justificacion': forms.Textarea(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Ingrese el motivo de la justificación...',
                'id': 'id_justificacion'
            }),
        }