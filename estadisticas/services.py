# estadisticas/services.py
from django.db import models
from django.utils import timezone
from .models import EstadisticaGlobal, EstadisticaPrograma
from estudiantes.models import Estudiante
from agenda.models import Sesion, AgendaEstudiante
from datetime import datetime, date

class CalculadorEstadisticas:
    
    @staticmethod
    def obtener_año_semestre_actual():
        """Determina año y semestre actual"""
        hoy = timezone.now().date()
        año = hoy.year
        semestre = '1' if hoy.month <= 6 else '2'
        return año, semestre
    
    @staticmethod
    def obtener_años_disponibles():
        """Obtiene lista de años desde 2025 hasta el año actual + 10 años"""
        año_actual = timezone.now().year
        años = list(range(2025, año_actual + 11))
        return años
    
    @staticmethod
    def obtener_periodos_disponibles():
        """Obtiene todos los periodos disponibles"""
        años = CalculadorEstadisticas.obtener_años_disponibles()
        semestres = ['1', '2']
        
        periodos = []
        for año in años:
            for semestre in semestres:
                periodos.append({
                    'año': año, 
                    'semestre': semestre
                })
        
        periodos.sort(key=lambda x: (-x['año'], -int(x['semestre'])))
        return periodos
    
    @staticmethod
    def calcular_todas_estadisticas():
        """Calcula estadísticas para TODOS los periodos disponibles de una vez"""
        periodos = CalculadorEstadisticas.obtener_periodos_disponibles()
        total_estadisticas = 0
        
        for periodo in periodos:
            año = periodo['año']
            semestre = periodo['semestre']
            
            print(f"🔄 Calculando estadísticas para {año}-S{semestre}...")
            
            # Calcular estadísticas globales
            global_stats = CalculadorEstadisticas.calcular_estadisticas_globales(año, semestre)
            
            # Calcular estadísticas de programas
            programas_stats = CalculadorEstadisticas.calcular_estadisticas_programas(año, semestre)
            
            total_estadisticas += 1
        
        print(f"🎉 Proceso completado: {total_estadisticas} periodos actualizados")
        return total_estadisticas
    
    @staticmethod
    def calcular_estadisticas_globales(año=None, semestre=None):
        """CORREGIDO: Calcula estadísticas globales para estudiantes ACTIVOS en el periodo"""
        if año is None or semestre is None:
            año, semestre = CalculadorEstadisticas.obtener_año_semestre_actual()
        
        print(f"📊 Calculando estadísticas globales para {año}-S{semestre}")
        
        # CORRECCIÓN: Filtrar estudiantes que estuvieron ACTIVOS en ese periodo
        if semestre == '1':
            fecha_inicio = datetime(año, 1, 1).date()
            fecha_fin = datetime(año, 6, 30).date()
        else:
            fecha_inicio = datetime(año, 7, 1).date()
            fecha_fin = datetime(año, 12, 31).date()
        
        # CORRECCIÓN: Estudiantes creados ANTES del fin del periodo (estuvieron activos)
        estudiantes_activos = Estudiante.objects.filter(
            created_at__date__lte=fecha_fin
        )
        total_estudiantes = estudiantes_activos.count()
        
        if total_estudiantes == 0:
            print(f"⚠️  No hay estudiantes activos para {año}-S{semestre}")
            # Crear estadísticas vacías pero no cero si hay estudiantes en el sistema
            total_sistema = Estudiante.objects.count()
            if total_sistema > 0:
                # Usar datos del sistema completo
                estudiantes_activos = Estudiante.objects.all()
                total_estudiantes = total_sistema
            else:
                return None
        
        # CORRECCIÓN: Calcular distribuciones de estudiantes ACTIVOS
        estudiantes_masculinos = estudiantes_activos.filter(genero='M').count()
        estudiantes_femeninos = estudiantes_activos.filter(genero='F').count()
        
        estudiantes_ifc = estudiantes_activos.filter(nivel='IFC').count()
        estudiantes_pcv = estudiantes_activos.filter(nivel='PCV').count()
        estudiantes_scp = estudiantes_activos.filter(nivel='SCP').count()
        
        # CORRECCIÓN: Agendas activas en el periodo
        agendas_activas = AgendaEstudiante.objects.filter(
            activo=True,
            fecha_inicio__lte=fecha_fin  # Agenda iniciada antes del fin del periodo
        )
        total_agendas_activas = agendas_activas.count()
        
        # CORRECCIÓN: Sesiones del periodo específico
        sesiones_periodo = Sesion.objects.filter(
            fecha_programada__range=[fecha_inicio, fecha_fin]
        )
        total_sesiones_completadas = sesiones_periodo.filter(estado='asistio').count()
        total_sesiones = sesiones_periodo.count()
        
        # Tasa de asistencia CORREGIDA
        tasa_asistencia = (total_sesiones_completadas / total_sesiones * 100) if total_sesiones > 0 else 0
        
        # Progreso y graduados CORREGIDOS
        promedio_progreso = agendas_activas.aggregate(
            models.Avg('sesiones_completadas')
        )['sesiones_completadas__avg'] or 0
        
        estudiantes_graduados = agendas_activas.filter(
            sesiones_completadas__gte=20  # Considerar "graduado" con 20+ sesiones
        ).count()
        
        # Crear o actualizar estadística
        estadistica, created = EstadisticaGlobal.objects.update_or_create(
            año=año,
            semestre=semestre,
            defaults={
                'total_estudiantes': total_estudiantes,
                'estudiantes_masculinos': estudiantes_masculinos,
                'estudiantes_femeninos': estudiantes_femeninos,
                'estudiantes_ifc': estudiantes_ifc,
                'estudiantes_pcv': estudiantes_pcv,
                'estudiantes_scp': estudiantes_scp,
                'total_agendas_activas': total_agendas_activas,
                'total_sesiones_completadas': total_sesiones_completadas,
                'tasa_asistencia_global': round(tasa_asistencia, 2),
                'promedio_progreso': round(promedio_progreso, 2),
                'estudiantes_graduados': estudiantes_graduados,
            }
        )
        
        print(f"✅ Estadísticas globales {'creadas' if created else 'actualizadas'} para {año}-S{semestre}")
        return estadistica
    
    @staticmethod
    def calcular_estadisticas_programas(año=None, semestre=None):
        """CORREGIDO: Estadísticas por programa para estudiantes ACTIVOS"""
        if año is None or semestre is None:
            año, semestre = CalculadorEstadisticas.obtener_año_semestre_actual()
        
        print(f"📈 Calculando estadísticas de programas para {año}-S{semestre}")
        
        # Determinar rango de fechas
        if semestre == '1':
            fecha_inicio = datetime(año, 1, 1).date()
            fecha_fin = datetime(año, 6, 30).date()
        else:
            fecha_inicio = datetime(año, 7, 1).date()
            fecha_fin = datetime(año, 12, 31).date()
        
        # CORRECCIÓN: Usar estudiantes activos en el periodo
        estudiantes_activos = Estudiante.objects.filter(
            created_at__date__lte=fecha_fin
        )
        
        # Agrupar estudiantes activos por programa
        programas_estudiantes = {}
        
        for estudiante in estudiantes_activos:
            programas = []
            
            # Obtener programas del estudiante
            if estudiante.programa_apoyo and isinstance(estudiante.programa_apoyo, list):
                programas = [p for p in estudiante.programa_apoyo if p and str(p).strip()]
            
            if not programas:
                programas = ["Sin Programa"]
            
            for programa in programas:
                programa_limpio = str(programa).strip()
                if programa_limpio not in programas_estudiantes:
                    programas_estudiantes[programa_limpio] = []
                programas_estudiantes[programa_limpio].append(estudiante.id)
        
        # Eliminar estadísticas existentes para este periodo
        EstadisticaPrograma.objects.filter(año=año, semestre=semestre).delete()
        
        # Crear estadísticas para cada programa
        estadisticas_creadas = 0
        for programa, estudiante_ids in programas_estudiantes.items():
            if estudiante_ids:
                total_estudiantes = len(estudiante_ids)
                
                # CORRECCIÓN: Obtener agendas y sesiones del periodo
                agendas = AgendaEstudiante.objects.filter(
                    estudiante_id__in=estudiante_ids,
                    activo=True
                )
                
                sesiones_totales = Sesion.objects.filter(
                    agenda__in=agendas,
                    fecha_programada__range=[fecha_inicio, fecha_fin]
                ).count()
                
                sesiones_completadas = Sesion.objects.filter(
                    agenda__in=agendas,
                    fecha_programada__range=[fecha_inicio, fecha_fin],
                    estado='asistio'
                ).count()
                
                # Calcular métricas
                tasa_completacion = (sesiones_completadas / sesiones_totales * 100) if sesiones_totales > 0 else 0
                promedio_sesiones = (sesiones_totales / total_estudiantes) if total_estudiantes > 0 else 0
                
                # Crear estadística
                try:
                    EstadisticaPrograma.objects.create(
                        programa=programa,
                        año=año,
                        semestre=semestre,
                        total_estudiantes=total_estudiantes,
                        sesiones_totales=sesiones_totales,
                        sesiones_completadas=sesiones_completadas,
                        tasa_completacion=round(tasa_completacion, 2),
                        promedio_sesiones_estudiante=round(promedio_sesiones, 2),
                    )
                    print(f"✅ {programa}: {total_estudiantes} estudiantes, {tasa_completacion:.1f}% completación")
                    estadisticas_creadas += 1
                except Exception as e:
                    print(f"❌ Error creando estadística para {programa}: {e}")
        
        print(f"🎉 {estadisticas_creadas} programas procesados para {año}-S{semestre}")
        return estadisticas_creadas
    
    @staticmethod
    def obtener_estadisticas_por_periodo(año, semestre):
        """Obtiene todas las estadísticas para un periodo específico"""
        try:
            estadistica_global = EstadisticaGlobal.objects.filter(año=año, semestre=semestre).first()
            estadisticas_programas = EstadisticaPrograma.objects.filter(año=año, semestre=semestre)
            
            return {
                'estadistica_global': estadistica_global,
                'estadisticas_programas': estadisticas_programas,
                'periodo': {'año': año, 'semestre': semestre}
            }
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas para {año}-S{semestre}: {e}")
            # Retornar estructura vacía en caso de error
            return {
                'estadistica_global': None,
                'estadisticas_programas': [],
                'periodo': {'año': año, 'semestre': semestre}
            }
    
    @staticmethod
    def obtener_periodo_actual():
        """Obtiene las estadísticas del periodo actual"""
        año, semestre = CalculadorEstadisticas.obtener_año_semestre_actual()
        return CalculadorEstadisticas.obtener_estadisticas_por_periodo(año, semestre)
    
    @staticmethod
    def actualizar_estadisticas_automatico():
        """Actualiza solo el periodo actual automáticamente"""
        try:
            año, semestre = CalculadorEstadisticas.obtener_año_semestre_actual()
            print(f"🔄 Actualización automática para {año}-S{semestre}")
            
            CalculadorEstadisticas.calcular_estadisticas_globales(año, semestre)
            CalculadorEstadisticas.calcular_estadisticas_programas(año, semestre)
        except Exception as e:
            print(f"⚠️ Error en actualización automática: {e}")