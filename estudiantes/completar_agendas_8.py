# estudiantes/completar_agendas_8.py

from estudiantes.models import Estudiante
from agenda.models import AgendaEstudiante, Sesion
from datetime import date, timedelta, time
import random

def completar_agendas_8_estudiantes():
    # Obtener estudiantes que tienen agenda
    estudiantes_con_agenda = Estudiante.objects.filter(agenda__isnull=False).distinct()
    
    if estudiantes_con_agenda.count() < 8:
        print(f"❌ No hay suficientes estudiantes con agenda. Encontrados: {estudiantes_con_agenda.count()}")
        return
    
    # Seleccionar aleatoriamente 8 estudiantes con agenda
    estudiantes_seleccionados = random.sample(list(estudiantes_con_agenda), 8)
    
    print(f"🎯 Completando 24 sesiones para {len(estudiantes_seleccionados)} estudiantes...")
    
    for i, estudiante in enumerate(estudiantes_seleccionados):
        try:
            agenda = AgendaEstudiante.objects.get(estudiante=estudiante)
            
            print(f"\n📋 Procesando estudiante {i+1}: {estudiante.nombres} {estudiante.apellido_paterno}")
            print(f"   📅 Agenda: {agenda.dia_semana} {agenda.hora_inicio.strftime('%H:%M')}-{agenda.hora_fin.strftime('%H:%M')}")
            print(f"   📊 Sesiones actuales: {agenda.sesiones_completadas}/{agenda.total_sesiones}")
            
            # Obtener todas las sesiones de la agenda
            sesiones = agenda.sesiones.all().order_by('fecha_programada')
            
            if sesiones.count() != 24:
                print(f"   ⚠️  Regenerando sesiones... (tenía {sesiones.count()}/24)")
                # Eliminar sesiones existentes y regenerar
                Sesion.objects.filter(agenda=agenda).delete()
                agenda.generar_sesiones()
                sesiones = agenda.sesiones.all().order_by('fecha_programada')
            
            # Marcar las 24 sesiones como completadas
            sesiones_completadas = 0
            for j, sesion in enumerate(sesiones):
                # Asignar estado "asistió" a todas las sesiones
                sesion.estado = 'asistio'
                sesion.observaciones = 'Sesión completada - Proceso automático'
                sesion.save()
                sesiones_completadas += 1
            
            # Actualizar el progreso de la agenda
            agenda.actualizar_progreso()
            agenda.refresh_from_db()
            
            print(f"   ✅ Sesiones completadas: {sesiones_completadas}/24")
            print(f"   🎉 Progreso actualizado: {agenda.sesiones_completadas}/{agenda.total_sesiones}")
            print(f"   📈 Estado: {agenda.get_estado_display()}")
            
        except AgendaEstudiante.DoesNotExist:
            print(f"❌ El estudiante {estudiante.nombres} {estudiante.apellido_paterno} no tiene agenda")
        except Exception as e:
            print(f"❌ Error con estudiante {i+1}: {estudiante.nombres} {estudiante.apellido_paterno}")
            print(f"   Error: {str(e)}")
    
    # Estadísticas finales
    print(f"\n🎉 RESUMEN FINAL:")
    print(f"   📋 Total estudiantes procesados: {len(estudiantes_seleccionados)}")
    
    agendas_completadas = AgendaEstudiante.objects.filter(sesiones_completadas=24).count()
    print(f"   ✅ Agendas completadas al 100%: {agendas_completadas}")
    
    # Mostrar los estudiantes procesados
    print(f"\n👥 ESTUDIANTES PROCESADOS:")
    for i, estudiante in enumerate(estudiantes_seleccionados, 1):
        agenda = AgendaEstudiante.objects.get(estudiante=estudiante)
        print(f"   {i}. {estudiante.nombres} {estudiante.apellido_paterno}")
        print(f"      📊 Progreso: {agenda.sesiones_completadas}/{agenda.total_sesiones} sesiones")
        print(f"      🎯 Estado: {agenda.get_estado_display()}")

def crear_y_completar_agendas_8_estudiantes():
    """Script alternativo: crear agenda y completar para estudiantes sin agenda"""
    
    # Obtener estudiantes sin agenda
    estudiantes_sin_agenda = Estudiante.objects.filter(agenda__isnull=True)
    
    if estudiantes_sin_agenda.count() < 8:
        print(f"❌ No hay suficientes estudiantes sin agenda. Encontrados: {estudiantes_sin_agenda.count()}")
        return
    
    # Seleccionar aleatoriamente 8 estudiantes sin agenda
    estudiantes_seleccionados = random.sample(list(estudiantes_sin_agenda), 8)
    
    print(f"🎯 Creando y completando agendas para {len(estudiantes_seleccionados)} estudiantes...")
    
    # Días y horarios disponibles
    dias_semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes']
    horarios = [
        {'inicio': time(8, 0), 'fin': time(9, 0)},
        {'inicio': time(9, 0), 'fin': time(10, 0)},
        {'inicio': time(10, 0), 'fin': time(11, 0)},
        {'inicio': time(11, 0), 'fin': time(12, 0)},
        {'inicio': time(14, 0), 'fin': time(15, 0)},
        {'inicio': time(15, 0), 'fin': time(16, 0)},
        {'inicio': time(16, 0), 'fin': time(17, 0)},
    ]
    
    for i, estudiante in enumerate(estudiantes_seleccionados):
        try:
            print(f"\n📋 Procesando estudiante {i+1}: {estudiante.nombres} {estudiante.apellido_paterno}")
            
            # Crear agenda
            dia_semana = random.choice(dias_semana)
            horario = random.choice(horarios)
            
            # Fecha de inicio (hace 6 meses para simular historial)
            fecha_inicio = date.today() - timedelta(days=180)
            
            # Ajustar al día de la semana correcto
            dias_numeros = {'lunes': 0, 'martes': 1, 'miercoles': 2, 'jueves': 3, 'viernes': 4}
            dia_objetivo = dias_numeros[dia_semana]
            while fecha_inicio.weekday() != dia_objetivo:
                fecha_inicio += timedelta(days=1)
            
            agenda = AgendaEstudiante.objects.create(
                estudiante=estudiante,
                dia_semana=dia_semana,
                hora_inicio=horario['inicio'],
                hora_fin=horario['fin'],
                fecha_inicio=fecha_inicio,
                total_sesiones=24,
                sesiones_completadas=0,
                activo=True
            )
            
            print(f"   ✅ Agenda creada: {dia_semana} {horario['inicio'].strftime('%H:%M')}-{horario['fin'].strftime('%H:%M')}")
            
            # Generar sesiones
            sesiones_generadas = agenda.generar_sesiones()
            print(f"   📊 Sesiones generadas: {sesiones_generadas}/24")
            
            # Marcar todas las sesiones como completadas
            sesiones = agenda.sesiones.all().order_by('fecha_programada')
            for sesion in sesiones:
                sesion.estado = 'asistio'
                sesion.observaciones = 'Sesión completada - Proceso automático'
                sesion.save()
            
            # Actualizar progreso
            agenda.actualizar_progreso()
            agenda.refresh_from_db()
            
            print(f"   🎉 Progreso final: {agenda.sesiones_completadas}/{agenda.total_sesiones}")
            print(f"   📈 Estado: {agenda.get_estado_display()}")
            
        except Exception as e:
            print(f"❌ Error con estudiante {i+1}: {estudiante.nombres} {estudiante.apellido_paterno}")
            print(f"   Error: {str(e)}")
    
    print(f"\n🎉 PROCESO COMPLETADO:")
    print(f"   📋 Total estudiantes procesados: {len(estudiantes_seleccionados)}")

if __name__ == "__main__":
    # Ejecutar la función que prefieras:
    
    # Opción 1: Para estudiantes que YA tienen agenda
    completar_agendas_8_estudiantes()
    
    # Opción 2: Para estudiantes SIN agenda (crear y completar)
    # crear_y_completar_agendas_8_estudiantes()