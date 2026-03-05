from django import forms
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from .models import Estudiante, Tutor, EVALUACION_CHOICES, PROGRAMA_CHOICES,SEMESTRE_CHOICES,GESTION_CHOICES

digits_validator = RegexValidator(r'^\d+$', 'Este campo solo admite números.')

class TutorForm(forms.ModelForm):
    
    telefono = forms.CharField(required=False, validators=[digits_validator], help_text="Campo opcional")
    celular = forms.CharField(required=False, validators=[digits_validator], help_text="Campo obligatorio")
    
    # Campo edad para tutor (18-110 años)
    edad_tutor = forms.IntegerField(
        validators=[MinValueValidator(18), MaxValueValidator(110)],
        help_text="Campo obligatorio - Edad entre 18 y 110 años"
    )
    

    class Meta:
        model = Tutor
        fields = [
            'apellido_paterno', 'apellido_materno', 'nombres', 'ci', 'parentesco',
            'ocupacion', 'zona', 'avenida', 'nro_vivienda', 'telefono', 'celular'
        ]
        help_texts = {
            'apellido_paterno': 'Campo obligatorio',
            'apellido_materno': 'Campo opcional',
            'nombres': 'Campo obligatorio',
            'ci': 'Campo obligatorio - Documento de identidad',
            'parentesco': 'Campo obligatorio',
            'ocupacion': 'Campo obligatorio',
            'zona': 'Campo obligatorio',
            'avenida': 'Campo obligatorio',
            'nro_vivienda': 'Campo obligatorio',
        }

    def clean_apellido_paterno(self): 
        return self.cleaned_data['apellido_paterno'].upper().strip()
    
    def clean_apellido_materno(self):
        val = self.cleaned_data.get('apellido_materno')
        return val.upper().strip() if val else val
    
    def clean_nombres(self): 
        return self.cleaned_data['nombres'].upper().strip()


class EstudianteForm(forms.ModelForm):
    
    telefono = forms.CharField(required=False, validators=[digits_validator], help_text="Campo opcional")
    celular = forms.CharField(required=False, validators=[digits_validator], help_text="Campo obligatorio")
    
    # Campo edad para estudiante (1-18 años)
    edad = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(18)],
        help_text="Campo obligatorio - Edad entre 1 y 18 años"
    )
    semestre = forms.ChoiceField(
        choices=SEMESTRE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        initial='1',
        help_text="Campo obligatorio - Seleccione el semestre"
    )
    maestra_aula = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nombre de la maestra/o de aula'
        }),
        help_text="Campo opcional"
    )
    gestion_ingreso = forms.ChoiceField(
        choices=GESTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        initial='2024',
        help_text="Campo obligatorio - Seleccione la gestión"
    )

    resultados_evaluacion = forms.MultipleChoiceField(
        choices=EVALUACION_CHOICES, 
        widget=forms.CheckboxSelectMultiple, 
        required=False,
        help_text="Campo obligatorio"
    )
    
    # NUEVO CAMPO PARA EVALUACIÓN MULTIDISCIPLINARIA
    evaluacion_requerida = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Especifique la evaluación multidisciplinaria requerida',
            'class': 'form-input'
        }),
        help_text="Campo condicional - Complete solo si seleccionó 'Evaluación Multidisciplinaria'"
    )
    
    programa_apoyo = forms.MultipleChoiceField(
        choices=PROGRAMA_CHOICES, 
        widget=forms.CheckboxSelectMultiple, 
        required=False,
        help_text="Campo obligatorio, seleccione al menos una opción"
    )

    class Meta:
        model = Estudiante
        exclude = ['created_at', 'updated_at', 'tutor']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'apellido_paterno': forms.TextInput(attrs={'class': 'form-input'}),
            'apellido_materno': forms.TextInput(attrs={'class': 'form-input'}),
            'nombres': forms.TextInput(attrs={'class': 'form-input'}),
        }
        help_texts = {
            'apellido_paterno': 'Campo obligatorio',
            'apellido_materno': 'Campo opcional',
            'nombres': 'Campo obligatorio',
            'fecha_nacimiento': 'Campo obligatorio',
            'genero': 'Campo obligatorio',
            'documento_identidad': 'Campo obligatorio - Documento de identidad',
            'codigo_rude': 'Campo obligatorio - Código RUDE',
            'pais': 'Campo obligatorio',
            'departamento': 'Campo obligatorio',
            'colegio_procedencia': 'Campo obligatorio',
            'grado': 'Campo obligatorio - Seleccione el grado',
            'zona': 'Campo obligatorio',
            'avenida': 'Campo obligatorio',
            'nro_vivienda': 'Campo obligatorio',
            'modalidad_atencion': 'Campo obligatorio, seleccione la modalidad'
        }

    # NUEVO MÉTODO CLEAN PARA VALIDACIÓN
    def clean(self):
        cleaned_data = super().clean()
        resultados_evaluacion = cleaned_data.get('resultados_evaluacion', [])
        evaluacion_requerida = cleaned_data.get('evaluacion_requerida', '')
        
        # Si seleccionó multidisciplinaria pero no completó el campo
        if 'multidisciplinaria' in resultados_evaluacion and not evaluacion_requerida:
            self.add_error('evaluacion_requerida', 'Debe especificar la evaluación multidisciplinaria requerida')
        
        # Si no seleccionó multidisciplinaria pero completó el campo, lo limpiamos
        if 'multidisciplinaria' not in resultados_evaluacion and evaluacion_requerida:
            cleaned_data['evaluacion_requerida'] = ''
            
        return cleaned_data

    def clean_apellido_paterno(self): 
        return self.cleaned_data['apellido_paterno'].upper().strip()
    
    def clean_apellido_materno(self):
        val = self.cleaned_data.get('apellido_materno')
        return val.upper().strip() if val else val
    
    def clean_nombres(self): 
        return self.cleaned_data['nombres'].upper().strip()
    
    def clean_pais(self): 
        return self.cleaned_data['pais'].upper().strip()
    
    def clean_departamento(self): 
        return self.cleaned_data['departamento'].upper().strip()
    
    def clean_colegio_procedencia(self):
        val = self.cleaned_data.get('colegio_procedencia')
        return val.upper().strip() if val else val
    
    def clean_zona(self): 
        return self.cleaned_data['zona'].upper().strip()
    
    def clean_avenida(self):
        val = self.cleaned_data.get('avenida')
        return val.upper().strip() if val else val

    def save(self, commit=True):
        inst = super().save(commit=False)
        inst.resultados_evaluacion = self.cleaned_data.get('resultados_evaluacion', [])
        inst.programa_apoyo = self.cleaned_data.get('programa_apoyo', [])
        
        # NUEVA LÓGICA PARA EVALUACIÓN REQUERIDA
        if 'multidisciplinaria' not in self.cleaned_data.get('resultados_evaluacion', []):
            inst.evaluacion_requerida = 'Ninguna'
        
        if commit: 
            inst.save()
        return inst