# estadisticas/admin.py
from django.contrib import admin
from .models import EstadisticaGlobal, EstadisticaPrograma

@admin.register(EstadisticaGlobal)
class EstadisticaGlobalAdmin(admin.ModelAdmin):
    list_display = ['año', 'semestre', 'total_estudiantes', 'total_agendas_activas', 'tasa_asistencia_global', 'estudiantes_graduados']
    list_filter = ['año', 'semestre']
    readonly_fields = ['fecha_calculo']
    ordering = ['-año', '-semestre']
    search_fields = ['año']

@admin.register(EstadisticaPrograma)
class EstadisticaProgramaAdmin(admin.ModelAdmin):
    list_display = ['programa', 'año', 'semestre', 'total_estudiantes', 'tasa_completacion']
    list_filter = ['año', 'semestre', 'programa']
    readonly_fields = ['fecha_actualizacion']
    ordering = ['-año', '-semestre', 'programa']
    search_fields = ['programa', 'año']