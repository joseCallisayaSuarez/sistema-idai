from django.db import models
from estudiantes.models import Estudiante
from datetime import timedelta

class AgendaEstudiante(models.Model):
    DIAS_SEMANA = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
    ]

    estudiante = models.OneToOneField(Estudiante, on_delete=models.CASCADE, related_name='agenda')
    dia_semana = models.CharField(max_length=10, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    fecha_inicio = models.DateField()
    total_sesiones = models.IntegerField(default=24)
    sesiones_completadas = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['estudiante__apellido_paterno']
        verbose_name = 'Agenda de Estudiante'
        verbose_name_plural = 'Agendas de Estudiantes'

    def __str__(self):
        return f"Agenda: {self.estudiante} - {self.dia_semana}"

    def generar_sesiones(self):
        """Genera las 24 sesiones automáticamente - VERSIÓN CORREGIDA"""
        from datetime import timedelta
        
        try:
            print(f"DEBUG: Iniciando generación de sesiones para {self.estudiante}")
            print(f"DEBUG: Fecha inicio: {self.fecha_inicio}, Día: {self.dia_semana}")
            
            # Eliminar sesiones existentes (por si hay recreación)
            Sesion.objects.filter(agenda=self).delete()
            print("DEBUG: Sesiones anteriores eliminadas")

            # Mapeo de días a números de weekday (0=lunes, 1=martes, etc.)
            dias_numeros = {
                'lunes': 0,
                'martes': 1, 
                'miercoles': 2,
                'jueves': 3,
                'viernes': 4,
            }
            
            # Obtener el número del día objetivo
            dia_objetivo = dias_numeros.get(self.dia_semana.lower())
            if dia_objetivo is None:
                print(f"ERROR: Día no válido: {self.dia_semana}")
                return 0

            # Empezar desde la fecha de inicio
            fecha_actual = self.fecha_inicio
            sesiones_creadas = 0
            
            # Encontrar la primera fecha que coincida con el día de la semana
            while fecha_actual.weekday() != dia_objetivo:
                fecha_actual += timedelta(days=1)
            
            print(f"DEBUG: Primera sesión programada para: {fecha_actual}")

            # Generar exactamente 24 sesiones
            for i in range(24):
                try:
                    # Verificar si ya existe una sesión en esta fecha (por seguridad)
                    if not Sesion.objects.filter(agenda=self, fecha_programada=fecha_actual).exists():
                        Sesion.objects.create(
                            agenda=self,
                            fecha_programada=fecha_actual,
                            estado='programada'
                        )
                        sesiones_creadas += 1
                        print(f"DEBUG: Sesión {i+1} creada para {fecha_actual}")
                    else:
                        print(f"DEBUG: Sesión ya existe para {fecha_actual}")
                    
                    # Avanzar exactamente 7 días para la siguiente sesión
                    fecha_actual += timedelta(days=7)
                    
                except Exception as e:
                    print(f"ERROR en sesión {i+1}: {str(e)}")
                    # Continuar con la siguiente fecha aunque falle una
                    fecha_actual += timedelta(days=7)
                    continue

            print(f"DEBUG: Total de sesiones creadas: {sesiones_creadas}/24")
            return sesiones_creadas
            
        except Exception as e:
            print(f"ERROR general en generar_sesiones: {str(e)}")
            return 0

    def get_progreso_porcentaje(self):
        """Calcula el porcentaje de progreso de las sesiones"""
        if self.total_sesiones == 0:
            return 0
        return (self.sesiones_completadas / self.total_sesiones) * 100

    def get_estado_display(self):
        """Devuelve el estado de la agenda con iconos"""
        if not self.activo:
            return "❌ Inactiva"
        elif self.sesiones_completadas == self.total_sesiones:
            return "🎉 Completada"
        else:
            return "✅ Activa"

    def get_sesiones_restantes(self):
        """Calcula cuántas sesiones faltan por completar"""
        return self.total_sesiones - self.sesiones_completadas

    def actualizar_progreso(self):
        """Actualiza el contador de sesiones completadas"""
        self.sesiones_completadas = self.sesiones.filter(estado='asistio').count()
        self.save()

class Sesion(models.Model):
    ESTADOS = [
        ('programada', '🟡 Programada'),
        ('asistio', '🟢 Asistió'),
        ('ausente', '🔴 Ausente'),
        ('justificada', '🟠 Justificada'),
    ]

    agenda = models.ForeignKey(AgendaEstudiante, on_delete=models.CASCADE, related_name='sesiones')
    fecha_programada = models.DateField()
    estado = models.CharField(max_length=15, choices=ESTADOS, default='programada')
    
    # NUEVOS CAMPOS SEPARADOS
    progreso = models.IntegerField(
        blank=True, 
        null=True,
        verbose_name="Calificación (1-10)",
        help_text="Calificación del progreso en la sesión (1-10)"
    )
    observaciones = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Observaciones de la Sesión",
        help_text="Notas y observaciones generales del desempeño del estudiante"
    )
    justificacion = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Motivo de Justificación",
        help_text="Descripción del motivo de la justificación (solo para ausencias justificadas)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_programada']
        unique_together = ['agenda', 'fecha_programada']
        verbose_name = 'Sesión'
        verbose_name_plural = 'Sesiones'

    def __str__(self):
        return f"Sesión: {self.agenda.estudiante} - {self.fecha_programada}"

    def get_estudiante(self):
        """Método helper para obtener el estudiante"""
        return self.agenda.estudiante

    def get_horario(self):
        """Devuelve el horario de la sesión"""
        return f"{self.agenda.hora_inicio.strftime('%H:%M')} - {self.agenda.hora_fin.strftime('%H:%M')}"

    def es_pasada(self):
        """Verifica si la sesión ya pasó (fecha anterior a hoy)"""
        from datetime import date
        return self.fecha_programada < date.today()

    def es_hoy(self):
        """Verifica si la sesión es para hoy"""
        from datetime import date
        return self.fecha_programada == date.today()

    def puede_registrar_asistencia(self):
        """Verifica si se puede registrar asistencia (sesión programada o hoy)"""
        from datetime import date
        return self.estado == 'programada' or self.fecha_programada <= date.today()

    def reprogramar(self, nueva_fecha):
        """Reprograma la sesión para una nueva fecha"""
        try:
            # Verificar que no exista ya una sesión en esa fecha
            if not Sesion.objects.filter(agenda=self.agenda, fecha_programada=nueva_fecha).exists():
                Sesion.objects.create(
                    agenda=self.agenda,
                    fecha_programada=nueva_fecha,
                    estado='programada',
                    observaciones=f"Reprogramación: {self.justificacion or 'Sin justificación'}"
                )
                return True
            return False
        except Exception as e:
            print(f"Error al reprogramar sesión: {e}")
            return False

    def get_progreso_display(self):
        """Devuelve el progreso con formato"""
        if self.progreso:
            return f"{self.progreso}/10"
        return "No evaluado"

# Señales para actualizar automáticamente el progreso
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Sesion)
def actualizar_progreso_despues_guardar(sender, instance, **kwargs):
    """Actualiza el progreso de la agenda cuando se guarda una sesión"""
    try:
        instance.agenda.actualizar_progreso()
    except Exception as e:
        print(f"Error actualizando progreso: {e}")

@receiver(post_delete, sender=Sesion)
def actualizar_progreso_despues_eliminar(sender, instance, **kwargs):
    """Actualiza el progreso de la agenda cuando se elimina una sesión"""
    try:
        instance.agenda.actualizar_progreso()
    except Exception as e:
        print(f"Error actualizando progreso: {e}")