# estadisticas/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from estudiantes.models import Estudiante
from agenda.models import Sesion, AgendaEstudiante
from .services import CalculadorEstadisticas

@receiver([post_save, post_delete], sender=Estudiante)
@receiver([post_save, post_delete], sender=Sesion)
@receiver([post_save, post_delete], sender=AgendaEstudiante)
def actualizar_estadisticas_automatico(sender, **kwargs):
    """Actualiza estadísticas automáticamente cuando cambian datos importantes"""
    try:
        CalculadorEstadisticas.actualizar_estadisticas_automatico()
    except Exception as e:
        print(f"⚠️ Error en actualización automática: {e}")

# En estadisticas/__init__.py agrega:
# default_app_config = 'estadisticas.apps.EstadisticasConfig'