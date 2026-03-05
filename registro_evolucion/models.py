# registro_evolucion/models.py
from django.db import models
from estudiantes.models import Estudiante
from django.contrib.auth import get_user_model

User = get_user_model()

class AreaDesarrollo(models.Model):
    """Modelo para áreas de desarrollo predefinidas"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Área de Desarrollo"
        verbose_name_plural = "Áreas de Desarrollo"
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre

class InformeFinal(models.Model):
    # Datos institucionales (constantes)
    departamento = models.CharField(max_length=100, default="LA PAZ")
    distrito_educativo = models.CharField(max_length=100, default="LA PAZ - 2")
    nombre_cee = models.CharField(max_length=200, default="ADAPTACIÓN INFANTIL")
    codigo_cee = models.CharField(max_length=20, default="80730696")
    codigo_edif_esc = models.CharField(max_length=20, default="80730433")
    codigo_sie = models.CharField(max_length=20, default="80730696")
    fundacion = models.CharField(max_length=50, default="6 de julio de 1966")
    ra_numero = models.CharField(max_length=50, default="1753/2021")
    
    # Datos del estudiante (automáticos)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='informes_finales')
    fecha_nacimiento = models.DateField(blank=True, null=True)
    edad = models.IntegerField(blank=True, null=True)
    grado = models.CharField(max_length=100, blank=True)
    codigo_rude = models.CharField(max_length=50, blank=True)
    
    # Datos del programa
    diagnostico_educativo = models.TextField(blank=True)
    semestre_programa = models.CharField(max_length=50, choices=[
        ('PRIMER SEMESTRE', 'PRIMER SEMESTRE'),
        ('SEGUNDO SEMESTRE', 'SEGUNDO SEMESTRE')
    ], default="PRIMER SEMESTRE")
    gestion = models.CharField(max_length=4, default="2025")
    
    # Informe de progresión
    otras_senales_alerta = models.TextField(blank=True, verbose_name="Otras Señales de Alerta")
    estado_final = models.CharField(max_length=200, blank=True, verbose_name="Estado Final")
    
    # Calificación de progreso (nuevos campos)
    promedio_progreso = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Promedio de Progreso (0-10)"
    )
    recomendacion_sesiones = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Recomendación de Sesiones"
    )
    
    # Estadísticas de sesiones (automáticas)
    total_sesiones = models.IntegerField(default=0)
    total_licencias = models.IntegerField(default=0)
    total_faltas = models.IntegerField(default=0)
    sesiones_asistidas = models.IntegerField(default=0)
    sesiones_evaluadas = models.IntegerField(default=0, verbose_name="Sesiones con Calificación")
    
    # Datos de registro
    docente = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Docente D.A.")
    director = models.CharField(max_length=200, blank=True, verbose_name="Director")
    sello_direccion = models.BooleanField(default=False, verbose_name="Sello Dirección C.E.E.")
    lugar_fecha = models.CharField(max_length=100, default="La Paz, noviembre de 2025")
    
    # Control
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=[
        ('BORRADOR', 'Borrador'),
        ('COMPLETADO', 'Completado'),
        ('APROBADO', 'Aprobado')
    ], default='BORRADOR')
    
    class Meta:
        verbose_name = "Informe Final"
        verbose_name_plural = "Informes Finales"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Informe Final - {self.estudiante} - {self.gestion}"
    
    def save(self, *args, **kwargs):
        # Llenar automáticamente datos del estudiante
        if self.estudiante:
            self.fecha_nacimiento = self.estudiante.fecha_nacimiento
            self.edad = self.estudiante.edad
            self.grado = f"{self.estudiante.grado} {self.estudiante.nivel}"
            self.codigo_rude = self.estudiante.codigo_rude
            
            # Calcular estadísticas de sesiones automáticamente
            self.calcular_estadisticas_sesiones()
            
            # Calcular sesiones asistidas
            self.sesiones_asistidas = self.total_sesiones - self.total_faltas - self.total_licencias
            
            # Calcular calificación de progreso
            self.calcular_calificacion_progreso()
        
        super().save(*args, **kwargs)
    
    def calcular_estadisticas_sesiones(self):
        """Calcula automáticamente las estadísticas de sesiones del estudiante"""
        try:
            from agenda.models import Sesion
            sesiones_estudiante = Sesion.objects.filter(
                agenda__estudiante=self.estudiante
            )
            
            self.total_sesiones = sesiones_estudiante.count()
            self.sesiones_asistidas = sesiones_estudiante.filter(estado='asistio').count()
            self.total_faltas = sesiones_estudiante.filter(estado='ausente').count()
            self.total_licencias = sesiones_estudiante.filter(estado='justificada').count()
            
        except Exception as e:
            print(f"Error calculando estadísticas de sesiones: {e}")
            # Si no existe el modelo Sesion, mantener valores por defecto
            pass
    
    def calcular_calificacion_progreso(self):
        """Calcula el promedio de progreso basado en las sesiones asistidas"""
        try:
            from agenda.models import Sesion
            
            # Obtener todas las sesiones asistidas del estudiante que tengan calificación
            sesiones_asistidas = Sesion.objects.filter(
                agenda__estudiante=self.estudiante,
                estado='asistio',
                progreso__isnull=False
            ).exclude(progreso__exact=0)
            
            self.sesiones_evaluadas = sesiones_asistidas.count()
            
            if self.sesiones_evaluadas > 0:
                # Calcular promedio de calificaciones
                total_calificaciones = sum(sesion.progreso for sesion in sesiones_asistidas)
                self.promedio_progreso = total_calificaciones / self.sesiones_evaluadas
                
                # Determinar recomendación basada en el promedio
                if self.promedio_progreso < 5.0:
                    self.recomendacion_sesiones = "DEBE RETOMAR 24 SESIONES MÁS"
                else:
                    self.recomendacion_sesiones = "DE ALTA"
                    
                # Actualizar el estado final automáticamente
                if not self.estado_final:
                    if self.promedio_progreso < 5.0:
                        self.estado_final = "Requiere continuidad en el programa"
                    else:
                        self.estado_final = "Proceso completado satisfactoriamente"
                        
            else:
                self.promedio_progreso = 0.00
                self.recomendacion_sesiones = "SIN EVALUACIONES REGISTRADAS"
                if not self.estado_final:
                    self.estado_final = "Sin evaluaciones suficientes para determinar progreso"
                
        except Exception as e:
            print(f"Error calculando calificación de progreso: {e}")
            # En caso de error, establecer valores por defecto
            self.promedio_progreso = 0.00
            self.recomendacion_sesiones = "ERROR EN CÁLCULO"
            if not self.estado_final:
                self.estado_final = "Error en cálculo de progreso"
    
    def get_promedio_display(self):
        """Devuelve el promedio formateado"""
        return f"{self.promedio_progreso:.2f}" if self.promedio_progreso else "0.00"
    
    def get_resumen_progreso(self):
        """Devuelve un resumen del progreso para mostrar en templates"""
        return {
            'promedio': self.get_promedio_display(),
            'recomendacion': self.recomendacion_sesiones,
            'sesiones_evaluadas': self.sesiones_evaluadas,
            'sesiones_totales': self.total_sesiones,
            'porcentaje_evaluado': (self.sesiones_evaluadas / self.total_sesiones * 100) if self.total_sesiones > 0 else 0
        }

class DesarrolloEducativo(models.Model):
    """Detalle de desarrollo educativo por área"""
    informe = models.ForeignKey(InformeFinal, on_delete=models.CASCADE, related_name='desarrollos')
    area = models.ForeignKey(AreaDesarrollo, on_delete=models.CASCADE)
    
    EVALUACION_OPCIONES = [
        ('NO_LOGRO', 'No Logró'),
        ('EN_PROCESO', 'En Proceso'),
        ('SI_LOGRO', 'Si Logró'),
    ]
    
    evaluacion = models.CharField(max_length=20, choices=EVALUACION_OPCIONES)
    recomendaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Desarrollo Educativo"
        verbose_name_plural = "Desarrollos Educativos"
        unique_together = ['informe', 'area']
    
    def __str__(self):
        return f"{self.area.nombre} - {self.informe.estudiante}"