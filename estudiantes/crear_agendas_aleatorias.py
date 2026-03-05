# estudiantes/crear_agendas_aleatorias.py

from estudiantes.models import Estudiante
from agenda.models import AgendaEstudiante, Sesion
from datetime import date, timedelta, time
import random

def crear_agendas_aleatorias():
    # Obtener todos los estudiantes (los 100 que creaste)
    estudiantes = Estudiante.objects.all()
    
    # Seleccionar aleatoriamente 80 estudiantes
    estudiantes_seleccionados = random.sample(list(estudiantes), 80)
    
    print(f"🎯 Creando agendas para {len(estudiantes_seleccionados)} estudiantes...")
    
    # Días de la semana disponibles
    dias_semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes']
    
    # Horarios típicos (mañana y tarde)
    horarios_manana = [
        {'inicio': time(8, 0), 'fin': time(9, 0)},
        {'inicio': time(9, 0), 'fin': time(10, 0)},
        {'inicio': time(10, 0), 'fin': time(11, 0)},
        {'inicio': time(11, 0), 'fin': time(12, 0)},
    ]
    
    horarios_tarde = [
        {'inicio': time(14, 0), 'fin': time(15, 0)},
        {'inicio': time(15, 0), 'fin': time(16, 0)},
        {'inicio': time(16, 0), 'fin': time(17, 0)},
        {'inicio': time(17, 0), 'fin': time(18, 0)},
    ]
    
    agendas_creadas = 0
    
    for i, estudiante in enumerate(estudiantes_seleccionados):
        try:
            # Verificar si el estudiante ya tiene agenda
            if AgendaEstudiante.objects.filter(estudiante=estudiante).exists():
                print(f"⏭️  Estudiante {i+1}: {estudiante.nombres} {estudiante.apellido_paterno} ya tiene agenda")
                continue
            
            # Seleccionar día aleatorio
            dia_semana = random.choice(dias_semana)
            
            # Seleccionar horario aleatorio (70% mañana, 30% tarde)
            if random.random() < 0.7:
                horario = random.choice(horarios_manana)
            else:
                horario = random.choice(horarios_tarde)
            
            # Fecha de inicio (entre 1 y 30 días en el futuro)
            dias_futuro = random.randint(1, 30)
            fecha_inicio = date.today() + timedelta(days=dias_futuro)
            
            # Ajustar la fecha para que coincida con el día de la semana seleccionado
            dias_numeros = {
                'lunes': 0,
                'martes': 1, 
                'miercoles': 2,
                'jueves': 3,
                'viernes': 4,
            }
            
            dia_objetivo = dias_numeros[dia_semana]
            while fecha_inicio.weekday() != dia_objetivo:
                fecha_inicio += timedelta(days=1)
            
            # Crear la agenda
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
            
            # Generar las sesiones automáticamente
            sesiones_generadas = agenda.generar_sesiones()
            
            # Simular progreso aleatorio en algunas agendas (30% tienen progreso)
            if random.random() < 0.3:
                # Completar entre 1 y 10 sesiones aleatoriamente
                sesiones_completar = random.randint(1, 10)
                sesiones = agenda.sesiones.all().order_by('fecha_programada')[:sesiones_completar]
                
                for sesion in sesiones:
                    # Asignar estado aleatorio (70% asistió, 20% ausente, 10% justificada)
                    probabilidad = random.random()
                    if probabilidad < 0.7:
                        sesion.estado = 'asistio'
                        sesion.observaciones = 'Asistencia registrada automáticamente'
                    elif probabilidad < 0.9:
                        sesion.estado = 'ausente'
                        sesion.observaciones = 'Ausencia sin justificación'
                    else:
                        sesion.estado = 'justificada'
                        sesion.observaciones = 'Justificado por enfermedad'
                    sesion.save()
                
                # Actualizar el progreso
                agenda.actualizar_progreso()
            
            agendas_creadas += 1
            print(f"✅ Agenda {i+1}: {estudiante.nombres} {estudiante.apellido_paterno}")
            print(f"   📅 {dia_semana.capitalize()} {horario['inicio'].strftime('%H:%M')}-{horario['fin'].strftime('%H:%M')}")
            print(f"   🗓️  Inicia: {fecha_inicio}")
            print(f"   📊 Sesiones: {sesiones_generadas}/24 generadas")
            
            if (i + 1) % 10 == 0:
                print(f"📈 Progreso: {i + 1}/{len(estudiantes_seleccionados)} estudiantes procesados")
                
        except Exception as e:
            print(f"❌ Error con estudiante {i+1}: {estudiante.nombres} {estudiante.apellido_paterno}")
            print(f"   Error: {str(e)}")
            continue
    
    # Estadísticas finales
    print(f"\n🎉 RESUMEN DE AGENDAS CREADAS:")
    print(f"   📋 Total estudiantes procesados: {len(estudiantes_seleccionados)}")
    print(f"   ✅ Agendas creadas exitosamente: {agendas_creadas}")
    print(f"   ⏭️  Estudiantes con agenda existente: {len(estudiantes_seleccionados) - agendas_creadas}")
    
    # Mostrar distribución por día
    print(f"\n📊 DISTRIBUCIÓN POR DÍA:")
    for dia in dias_semana:
        count = AgendaEstudiante.objects.filter(dia_semana=dia).count()
        print(f"   {dia.capitalize()}: {count} agendas")
    
    # Mostrar distribución por horario
    print(f"\n🕐 DISTRIBUCIÓN POR TURNO:")
    manana_count = AgendaEstudiante.objects.filter(hora_inicio__hour__lt=12).count()
    tarde_count = AgendaEstudiante.objects.filter(hora_inicio__hour__gte=12).count()
    print(f"   Mañana (8:00-12:00): {manana_count} agendas")
    print(f"   Tarde (14:00-18:00): {tarde_count} agendas")
    
    # Mostrar progreso general
    total_sesiones = sum(agenda.sesiones_completadas for agenda in AgendaEstudiante.objects.all())
    total_posibles = sum(agenda.total_sesiones for agenda in AgendaEstudiante.objects.all())
    print(f"\n📈 PROGRESO GENERAL:")
    print(f"   Sesiones completadas: {total_sesiones}")
    print(f"   Sesiones totales: {total_posibles}")
    print(f"   Progreso: {(total_sesiones/total_posibles*100 if total_posibles > 0 else 0):.1f}%")

if __name__ == "__main__":
    crear_agendas_aleatorias()