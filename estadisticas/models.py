# estadisticas/models.py
from django.db import models

class EstadisticaGlobal(models.Model):
    fecha_calculo = models.DateTimeField(auto_now=True)
    año = models.IntegerField()
    semestre = models.CharField(max_length=1, choices=[('1', 'Primer Semestre'), ('2', 'Segundo Semestre')])
    
    # Resumen General
    total_estudiantes = models.IntegerField(default=0)
    total_agendas_activas = models.IntegerField(default=0)
    total_sesiones_completadas = models.IntegerField(default=0)
    tasa_asistencia_global = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    estudiantes_graduados = models.IntegerField(default=0)
    promedio_progreso = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Distribución por género
    estudiantes_masculinos = models.IntegerField(default=0)
    estudiantes_femeninos = models.IntegerField(default=0)
    
    # Distribución por nivel
    estudiantes_ifc = models.IntegerField(default=0)
    estudiantes_pcv = models.IntegerField(default=0)
    estudiantes_scp = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Estadísticas Globales"
        ordering = ['-año', '-semestre']
        unique_together = ['año', 'semestre']

    def __str__(self):
        return f"Estadísticas {self.año}-S{self.semestre}"

class EstadisticaPrograma(models.Model):
    programa = models.CharField(max_length=100)
    año = models.IntegerField()
    semestre = models.CharField(max_length=1, choices=[('1', 'Primer Semestre'), ('2', 'Segundo Semestre')])
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    total_estudiantes = models.IntegerField(default=0)
    sesiones_totales = models.IntegerField(default=0)
    sesiones_completadas = models.IntegerField(default=0)
    tasa_completacion = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    promedio_sesiones_estudiante = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-año', '-semestre', 'programa']
        unique_together = ['programa', 'año', 'semestre']

    def __str__(self):
        return f"{self.programa} - {self.año}-S{self.semestre}"