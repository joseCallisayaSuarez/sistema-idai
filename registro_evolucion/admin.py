# registro_evolucion/admin.py
from django.contrib import admin
from .models import AreaDesarrollo, InformeFinal, DesarrolloEducativo

@admin.register(AreaDesarrollo)
class AreaDesarrolloAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'orden', 'activo']
    list_editable = ['orden', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']

class DesarrolloEducativoInline(admin.TabularInline):
    model = DesarrolloEducativo
    extra = 1
    fields = ['area', 'evaluacion', 'recomendaciones']

@admin.register(InformeFinal)
class InformeFinalAdmin(admin.ModelAdmin):
    list_display = ['estudiante', 'gestion', 'semestre_programa', 'docente', 'estado', 'fecha_creacion']
    list_filter = ['gestion', 'semestre_programa', 'docente', 'estado']
    search_fields = ['estudiante__nombres', 'estudiante__apellido_paterno', 'codigo_rude']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'total_sesiones', 'total_licencias', 'total_faltas', 'sesiones_asistidas']
    inlines = [DesarrolloEducativoInline]
    
    fieldsets = (
        ('Datos Institucionales', {
            'fields': (
                'departamento', 'distrito_educativo', 
                'nombre_cee', 'codigo_cee', 'codigo_edif_esc', 'codigo_sie',
                'fundacion', 'ra_numero', 'gestion'
            )
        }),
        ('Datos del Estudiante', {
            'fields': (
                'estudiante', 'fecha_nacimiento', 'edad',
                'grado', 'codigo_rude', 'diagnostico_educativo',
                'semestre_programa'
            )
        }),
        ('Informe de Progresión', {
            'fields': (
                'otras_senales_alerta', 'estado_final',
            )
        }),
        ('Estadísticas de Sesiones', {
            'fields': (
                'total_sesiones', 'total_licencias',
                'total_faltas', 'sesiones_asistidas'
            )
        }),
        ('Registro y Control', {
            'fields': (
                'docente', 'director', 'sello_direccion', 'lugar_fecha',
                'estado', 'fecha_creacion', 'fecha_actualizacion'
            )
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.estado == 'APROBADO':
            # Si el informe está aprobado, hacer todos los campos readonly
            return [field.name for field in obj._meta.fields]
        return self.readonly_fields