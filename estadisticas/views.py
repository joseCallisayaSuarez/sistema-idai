# estadisticas/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import EstadisticaGlobal, EstadisticaPrograma
from .services import CalculadorEstadisticas
from estudiantes.models import Estudiante
from agenda.models import Sesion
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string

from io import BytesIO


@login_required
def dashboard_estadisticas(request):
    """Dashboard completo de estadísticas con selector de periodo"""
    # Obtener periodo seleccionado o usar el actual
    año_seleccionado = request.GET.get('año')
    semestre_seleccionado = request.GET.get('semestre')
    
    if año_seleccionado and semestre_seleccionado:
        año = int(año_seleccionado)
        semestre = semestre_seleccionado
    else:
        año, semestre = CalculadorEstadisticas.obtener_año_semestre_actual()
    
    print(f"🚀 Cargando dashboard para {año}-S{semestre}")
    
    # Obtener estadísticas para el periodo seleccionado
    datos_periodo = CalculadorEstadisticas.obtener_estadisticas_por_periodo(año, semestre)
    
    # Si no hay estadísticas globales, crear unas vacías
    if not datos_periodo['estadistica_global']:
        print("📊 No hay estadísticas globales, creando vacías...")
        datos_periodo['estadistica_global'] = EstadisticaGlobal.objects.create(
            año=año,
            semestre=semestre,
            total_estudiantes=0,
            estudiantes_masculinos=0,
            estudiantes_femeninos=0,
            estudiantes_ifc=0,
            estudiantes_pcv=0,
            estudiantes_scp=0,
            total_agendas_activas=0,
            total_sesiones_completadas=0,
            tasa_asistencia_global=0,
            promedio_progreso=0,
            estudiantes_graduados=0
        )
    
    # Obtener periodos disponibles para el selector
    periodos_disponibles = CalculadorEstadisticas.obtener_periodos_disponibles()
    años_disponibles = CalculadorEstadisticas.obtener_años_disponibles()
    
    # Datos adicionales para tarjetas
    total_estudiantes = Estudiante.objects.count()
    sesiones_hoy = Sesion.objects.filter(fecha_programada=timezone.now().date()).count()
    
    context = {
        'estadistica_global': datos_periodo['estadistica_global'],
        'estadisticas_programas': datos_periodo['estadisticas_programas'],
        'periodo_actual': datos_periodo['periodo'],
        'periodos_disponibles': periodos_disponibles,
        'años_disponibles': años_disponibles,
        'total_estudiantes': total_estudiantes,
        'sesiones_hoy': sesiones_hoy,
    }
    
    return render(request, 'estadisticas/dashboard.html', context)

@login_required
def actualizar_estadisticas(request):
    """Forzar actualización de TODAS las estadísticas de una vez"""
    if request.method == 'POST':
        try:
            print("🔄 INICIANDO ACTUALIZACIÓN COMPLETA DE ESTADÍSTICAS...")
            
            # Calcular TODAS las estadísticas para TODOS los periodos
            periodos_actualizados = CalculadorEstadisticas.calcular_todas_estadisticas()
            
            # Obtener el periodo actual para redireccionar
            año_actual, semestre_actual = CalculadorEstadisticas.obtener_año_semestre_actual()
            
            messages.success(request, f'✅ ¡Actualización completada! {periodos_actualizados} periodos actualizados.')
            return redirect(f'/estadisticas/?año={año_actual}&semestre={semestre_actual}')
            
        except Exception as e:
            print(f"❌ Error en actualización completa: {e}")
            messages.error(request, f'❌ Error al actualizar estadísticas: {str(e)}')
            return redirect('estadisticas:dashboard_estadisticas')
    
    # Para GET, redirigir al dashboard
    return redirect('estadisticas:dashboard_estadisticas')


@login_required
def generar_pdf_estadisticas(request):
    """Generar PDF de estadísticas para el periodo actual"""
    # Obtener periodo seleccionado o usar el actual
    año_seleccionado = request.GET.get('año')
    semestre_seleccionado = request.GET.get('semestre')
    
    if año_seleccionado and semestre_seleccionado:
        año = int(año_seleccionado)
        semestre = semestre_seleccionado
    else:
        año, semestre = CalculadorEstadisticas.obtener_año_semestre_actual()
    
    # Obtener estadísticas para el periodo seleccionado
    datos_periodo = CalculadorEstadisticas.obtener_estadisticas_por_periodo(año, semestre)
    
    # Si no hay estadísticas globales, crear unas vacías
    if not datos_periodo['estadistica_global']:
        datos_periodo['estadistica_global'] = EstadisticaGlobal.objects.create(
            año=año,
            semestre=semestre,
            total_estudiantes=0,
            estudiantes_masculinos=0,
            estudiantes_femeninos=0,
            estudiantes_ifc=0,
            estudiantes_pcv=0,
            estudiantes_scp=0,
            total_agendas_activas=0,
            total_sesiones_completadas=0,
            tasa_asistencia_global=0,
            promedio_progreso=0,
            estudiantes_graduados=0
        )
    
    # Datos adicionales
    total_estudiantes = Estudiante.objects.count()
    
    context = {
        'estadistica_global': datos_periodo['estadistica_global'],
        'estadisticas_programas': datos_periodo['estadisticas_programas'],
        'periodo_actual': datos_periodo['periodo'],
        'total_estudiantes': total_estudiantes,
    }
    
    # Renderizar template HTML
    html_string = render_to_string('estadisticas/estadisticas_pdf.html', context)
    
    # Crear respuesta PDF para visualización en navegador
    response = HttpResponse(content_type='application/pdf')
    filename = f"estadisticas_{año}_s{semestre}.pdf"
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