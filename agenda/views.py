from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from datetime import date, timedelta
from .models import AgendaEstudiante, Sesion
from .forms import BuscarEstudianteForm, AgendaForm, SesionForm, AsistenciaForm
from estudiantes.models import Estudiante
from django.http import HttpResponse
from django.template.loader import render_to_string

from io import BytesIO
import os
import base64
from django.conf import settings


# PASO 1: Buscar estudiante por CI
def buscar_estudiante_agenda(request):
    estudiante = None
    agenda_existente = None
    
    if request.method == 'POST':
        form_busqueda = BuscarEstudianteForm(request.POST)
        if form_busqueda.is_valid():
            ci = form_busqueda.cleaned_data['ci_estudiante']
            
            # Buscar estudiante por CI
            estudiante = Estudiante.objects.filter(
                documento_identidad__icontains=ci
            ).first()
            
            if estudiante:
                # Verificar si ya tiene agenda
                agenda_existente = AgendaEstudiante.objects.filter(estudiante=estudiante).first()
            else:
                messages.error(request, '❌ No se encontró ningún estudiante con ese CI')
    else:
        form_busqueda = BuscarEstudianteForm()
    
    return render(request, 'agenda/buscar_estudiante.html', {
        'form_busqueda': form_busqueda,
        'estudiante': estudiante,
        'agenda_existente': agenda_existente
    })

# PASO 2: Crear agenda para el estudiante
# PASO 2: Crear agenda para el estudiante
def crear_agenda(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    
    # Verificar si ya tiene agenda
    if AgendaEstudiante.objects.filter(estudiante=estudiante).exists():
        messages.warning(request, '⚠️ Este estudiante ya tiene una agenda')
        return redirect('agenda:buscar_estudiante')
    
    if request.method == 'POST':
        form_agenda = AgendaForm(request.POST)
        if form_agenda.is_valid():
            agenda = form_agenda.save(commit=False)
            agenda.estudiante = estudiante
            agenda.save()
            
            # Generar las 24 sesiones automáticamente
            agenda.generar_sesiones()
            
            # Renderizar el template con una variable de contexto que indique éxito
            return render(request, 'agenda/crear_agenda.html', {
                'form_agenda': form_agenda,
                'estudiante': estudiante,
                'agenda_creada': True,  # ¡ESTA ES LA CLAVE!
                'agenda': agenda  # También pasamos la agenda creada
            })
        else:
            messages.error(request, '❌ Error al crear la agenda')
    else:
        form_agenda = AgendaForm()
    
    return render(request, 'agenda/crear_agenda.html', {
        'form_agenda': form_agenda,
        'estudiante': estudiante,
        'agenda_creada': False
    })
# PASO 3: Calendario general para ver todas las sesiones
def calendario_general(request):
    # Obtener fecha actual o del filtro
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    # Calcular primer y último día del mes
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    # Obtener sesiones del mes
    sesiones = Sesion.objects.filter(
        fecha_programada__range=[first_day, last_day]
    ).select_related('agenda__estudiante')
    
    # Crear estructura del calendario correctamente
    calendario = []
    
    # Encontrar el primer lunes del mes (o el primer día si empieza en lunes)
    current_day = first_day
    # Retroceder hasta el lunes anterior si el mes no empieza en lunes
    while current_day.weekday() != 0:  # 0 es lunes
        current_day -= timedelta(days=1)
    
    # Avanzar hasta el último domingo del mes
    last_calendar_day = last_day
    while last_calendar_day.weekday() != 6:  # 6 es domingo
        last_calendar_day += timedelta(days=1)
    
    # Llenar el calendario (6 semanas máximo)
    while current_day <= last_calendar_day:
        dia_sesiones = sesiones.filter(fecha_programada=current_day)
        calendario.append({
            'fecha': current_day,
            'sesiones': dia_sesiones,
            'es_hoy': current_day == date.today(),
            'es_del_mes': first_day.month == current_day.month  # Para diferenciar días del mes actual
        })
        current_day += timedelta(days=1)
    
    # Navegación de meses
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    return render(request, 'agenda/calendario_general.html', {
        'calendario': calendario,
        'mes_actual': month,
        'año_actual': year,
        'nombre_mes': first_day.strftime('%B').capitalize(),
        'mes_anterior': prev_month,
        'año_anterior': prev_year,
        'mes_siguiente': next_month,
        'año_siguiente': next_year,
        'hoy': date.today()
    })

# PASO 4: Registrar asistencia - VERSIÓN CORREGIDA CON PROGRESO
def registrar_asistencia(request, sesion_id):
    sesion = get_object_or_404(Sesion, id=sesion_id)
    
    if request.method == 'POST':
        # Usar el formulario AsistenciaForm que incluye el campo progreso
        form = AsistenciaForm(request.POST, instance=sesion)
        if form.is_valid():
            sesion_actualizada = form.save()
            
            # Validar rango del progreso si se proporciona
            progreso = form.cleaned_data.get('progreso')
            if progreso and (progreso < 1 or progreso > 10):
                messages.error(request, '❌ El progreso debe estar entre 1 y 10')
                return render(request, 'agenda/registrar_asistencia.html', {
                    'form': form,
                    'sesion': sesion,
                    'current_year': request.POST.get('year', date.today().year),
                    'current_month': request.POST.get('month', date.today().month),
                })
            
            # Si es justificada, reprogramar
            if sesion_actualizada.estado == 'justificada':
                reprogramar_sesion(sesion_actualizada)
            
            messages.success(request, '✅ Asistencia registrada correctamente')
            
            # Redirección correcta al calendario
            year = request.POST.get('year') or str(date.today().year)
            month = request.POST.get('month') or str(date.today().month)
            
            from django.urls import reverse
            redirect_url = reverse('agenda:calendario_general') + f'?year={year}&month={month}'
            return redirect(redirect_url)
        else:
            messages.error(request, '❌ Error en el formulario')
    else:
        # GET request - mostrar formulario con instancia
        form = AsistenciaForm(instance=sesion)
    
    context = {
        'form': form,
        'sesion': sesion,
        'current_year': request.GET.get('year', date.today().year),
        'current_month': request.GET.get('month', date.today().month),
    }
    return render(request, 'agenda/registrar_asistencia.html', context)

# Función para reprogramar sesiones justificadas
def reprogramar_sesion(sesion_justificada):
    try:
        nueva_fecha = sesion_justificada.fecha_programada + timedelta(days=7)
        
        # Verificar si no existe ya una sesión en esa fecha
        if not Sesion.objects.filter(agenda=sesion_justificada.agenda, fecha_programada=nueva_fecha).exists():
            Sesion.objects.create(
                agenda=sesion_justificada.agenda,
                fecha_programada=nueva_fecha,
                estado='programada',
                observaciones=f"Reprogramación: {sesion_justificada.observaciones}"
            )
            return True
        return False
    except Exception as e:
        print(f"Error al reprogramar sesión: {e}")
        return False

# Lista de todas las agendas
# Lista de todas las agendas
def lista_agendas(request):
    agendas = AgendaEstudiante.objects.all().select_related('estudiante')
    
    # FILTRAR POR BÚSQUEDA (ESTO ES LO QUE FALTA)
    query = request.GET.get('q', '')
    if query:
        agendas = agendas.filter(
            Q(estudiante__nombres__icontains=query) |
            Q(estudiante__apellido_paterno__icontains=query) |
            Q(estudiante__apellido_materno__icontains=query) |
            Q(estudiante__documento_identidad__icontains=query)
        )
    
    # Calcular estadísticas (DEBE IR DESPUÉS DEL FILTRADO)
    total_agendas = agendas.count()
    en_progreso = agendas.filter(sesiones_completadas__lt=24, activo=True).count()
    completadas = agendas.filter(sesiones_completadas=24).count()
    inactivas = agendas.filter(activo=False).count()
    
    return render(request, 'agenda/lista_agendas.html', {
        'agendas': agendas,
        'total_agendas': total_agendas,
        'en_progreso': en_progreso,
        'completadas': completadas,
        'inactivas': inactivas,
        'query': query  # Opcional: para pasar el término de búsqueda al template
    })

# CRUD COMPLETO PARA AGENDAS

# READ - Detalle de agenda
def detalle_agenda(request, agenda_id):
    agenda = get_object_or_404(AgendaEstudiante, id=agenda_id)
    sesiones = Sesion.objects.filter(agenda=agenda).order_by('fecha_programada')
    
    # Calcular promedio de progreso
    sesiones_con_progreso = sesiones.exclude(progreso__isnull=True)
    if sesiones_con_progreso.exists():
        promedio_progreso = sum(s.progreso for s in sesiones_con_progreso) / sesiones_con_progreso.count()
    else:
        promedio_progreso = None
    
    return render(request, 'agenda/detalle_agenda.html', {
        'agenda': agenda,
        'sesiones': sesiones,
        'promedio_progreso': promedio_progreso
    })

# UPDATE - Editar agenda
def editar_agenda(request, agenda_id):
    agenda = get_object_or_404(AgendaEstudiante, id=agenda_id)
    
    if request.method == 'POST':
        form = AgendaForm(request.POST, instance=agenda)
        if form.is_valid():
            # Guardar los cambios
            agenda_editada = form.save()
            
            # REGENERAR LAS SESIONES SIEMPRE al editar
            sesiones_regeneradas = agenda_editada.generar_sesiones()
            
            if sesiones_regeneradas == 24:
                messages.success(request, '✅ Agenda actualizada correctamente - 24 sesiones regeneradas')
            else:
                messages.warning(request, f'⚠️ Agenda actualizada - {sesiones_regeneradas}/24 sesiones regeneradas')
            
            return redirect('agenda:detalle_agenda', agenda_id=agenda.id)
        else:
            messages.error(request, '❌ Error al actualizar la agenda')
    else:
        form = AgendaForm(instance=agenda)
    
    return render(request, 'agenda/editar_agenda.html', {
        'form': form,
        'agenda': agenda
    })

# EDITAR SESIÓN INDIVIDUAL
def editar_sesion(request, sesion_id):
    sesion = get_object_or_404(Sesion, id=sesion_id)
    
    if request.method == 'POST':
        form = SesionForm(request.POST, instance=sesion)
        if form.is_valid():
            # Validar progreso si se proporciona
            progreso = form.cleaned_data.get('progreso')
            if progreso and (progreso < 1 or progreso > 10):
                messages.error(request, '❌ El progreso debe estar entre 1 y 10')
                return render(request, 'agenda/editar_sesion.html', {
                    'form': form,
                    'sesion': sesion
                })
            
            form.save()
            messages.success(request, '✅ Sesión actualizada correctamente')
            return redirect('agenda:detalle_agenda', agenda_id=sesion.agenda.id)
        else:
            messages.error(request, '❌ Error al actualizar la sesión')
    else:
        form = SesionForm(instance=sesion)
    
    return render(request, 'agenda/editar_sesion.html', {
        'form': form,
        'sesion': sesion
    })

# TOGGLE - Activar/Desactivar agenda
def desactivar_agenda(request, agenda_id):
    agenda = get_object_or_404(AgendaEstudiante, id=agenda_id)
    if request.method == 'POST':
        agenda.activo = False
        agenda.save()
        messages.success(request, '⏸️ Agenda pausada correctamente')
    return redirect('agenda:lista_agendas')

def activar_agenda(request, agenda_id):
    agenda = get_object_or_404(AgendaEstudiante, id=agenda_id)
    if request.method == 'POST':
        agenda.activo = True
        agenda.save()
        messages.success(request, '▶️ Agenda activada correctamente')
    return redirect('agenda:lista_agendas')

# DELETE - Eliminar agenda
def eliminar_agenda(request, agenda_id):
    agenda = get_object_or_404(AgendaEstudiante, id=agenda_id)
    if request.method == 'POST':
        estudiante_nombre = f"{agenda.estudiante.nombres} {agenda.estudiante.apellido_paterno}"
        agenda.delete()
        messages.success(request, f'🗑️ Agenda de {estudiante_nombre} eliminada correctamente')
    return redirect('agenda:lista_agendas')




def generar_pdf_agenda(request, agenda_id):
    agenda = get_object_or_404(AgendaEstudiante, id=agenda_id)
    sesiones = Sesion.objects.filter(agenda=agenda).order_by('fecha_programada')
    
    # Calcular promedio de progreso
    sesiones_con_progreso = sesiones.exclude(progreso__isnull=True)
    if sesiones_con_progreso.exists():
        promedio_progreso = sum(s.progreso for s in sesiones_con_progreso) / sesiones_con_progreso.count()
    else:
        promedio_progreso = None
    
    # Renderizar template HTML
    context = {
        'agenda': agenda,
        'sesiones': sesiones,
        'promedio_progreso': promedio_progreso
    }
    
    html_string = render_to_string('agenda/agenda_pdf.html', context)
    
    # Crear respuesta PDF para visualización en navegador
    response = HttpResponse(content_type='application/pdf')
    filename = f"agenda_{agenda.estudiante.documento_identidad}_{agenda.estudiante.apellido_paterno}.pdf"
    
    # CAMBIO IMPORTANTE: Usar 'inline' en lugar de 'attachment'
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    # Generar PDF con xhtml2pdf
    pdf = pisa.pisaDocument(
        BytesIO(html_string.encode("UTF-8")), 
        dest=response,
        encoding='UTF-8'
    )
    
    if pdf.err:
        return HttpResponse('Error al generar PDF: %s' % pdf.err)
    
    return response