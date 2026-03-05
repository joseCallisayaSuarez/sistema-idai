# registro_evolucion/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db import transaction, models
from .models import InformeFinal, AreaDesarrollo, DesarrolloEducativo
from .forms import InformeFinalForm, DesarrolloEducativoFormSet
from estudiantes.models import Estudiante
from django.template.loader import render_to_string

from io import BytesIO
import json
import os
import base64
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages


@login_required
def lista_informes_finales(request):
    """Lista todos los informes finales y estudiantes"""
    informes = InformeFinal.objects.all().order_by('-fecha_creacion')
    
    # TODOS los estudiantes pueden tener informes, sin restricción de sesiones
    todos_estudiantes = Estudiante.objects.all().order_by('apellido_paterno', 'nombres')
    
    context = {
        'informes': informes,
        'todos_estudiantes': todos_estudiantes,  # Cambiado el nombre para reflejar que son todos
        'titulo': 'Informes Finales'
    }
    return render(request, 'registro_evolucion/lista_informes.html', context)

@login_required
def crear_informe_final(request):
    """Crear nuevo informe final"""
    areas_desarrollo = AreaDesarrollo.objects.filter(activo=True).order_by('orden')
    
    if request.method == 'POST':
        form = InformeFinalForm(request.POST)
        formset = DesarrolloEducativoFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    informe = form.save(commit=False)
                    informe.docente = request.user
                    informe.save()
                    
                    # Guardar el formset
                    formset.instance = informe
                    formset.save()
                    
                    messages.success(request, '✅ Informe final creado correctamente')
                    return redirect('registro_evolucion:lista_informes')
                    
            except Exception as e:
                messages.error(request, f'❌ Error al crear informe: {str(e)}')
        else:
            messages.error(request, '❌ Por favor corrige los errores en el formulario')
    else:
        form = InformeFinalForm()
        formset = DesarrolloEducativoFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'areas_desarrollo': areas_desarrollo,
        'titulo': 'Nuevo Informe Final',
        'estudiantes': Estudiante.objects.all()
    }
    return render(request, 'registro_evolucion/form_informe.html', context)

@login_required
def editar_informe_final(request, pk):
    """Editar informe final existente - VERSIÓN COMPLETA CORREGIDA"""
    informe = get_object_or_404(InformeFinal, pk=pk)
    
    # Obtener los desarrollos existentes y crear diccionario
    desarrollos_existentes = informe.desarrollos.all().select_related('area')
    desarrollos_dict = {desarrollo.area_id: desarrollo for desarrollo in desarrollos_existentes}
    
    # RECALCULAR PROMEDIO (NUEVO)
    try:
        sesiones_asistidas = informe.estudiante.agenda.sesiones.filter(
            estado='asistio', 
            progreso__isnull=False
        ).exclude(progreso__exact=0)
        
        sesiones_evaluadas = sesiones_asistidas.count()
        if sesiones_evaluadas > 0:
            total_calificaciones = sum(sesion.progreso for sesion in sesiones_asistidas)
            promedio_progreso = total_calificaciones / sesiones_evaluadas
        else:
            promedio_progreso = 0.00
    except Exception as e:
        print(f"Error calculando promedio: {e}")
        promedio_progreso = 0.00
        sesiones_evaluadas = 0
    
    # INICIALIZAR form FUERA del bloque if
    form = InformeFinalForm(instance=informe)
    
    if request.method == 'POST':
        # Crear una copia mutable del POST data
        post_data = request.POST.copy()
        
        # Forzar el estudiante al que ya está asignado el informe
        post_data['estudiante'] = str(informe.estudiante.id)
        
        # Si no hay lugar_fecha, usar el valor por defecto
        if not post_data.get('lugar_fecha'):
            post_data['lugar_fecha'] = informe.lugar_fecha or "La Paz, noviembre de 2025"
        
        form = InformeFinalForm(post_data, instance=informe)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Guardar el informe principal
                    informe_actualizado = form.save(commit=False)
                    # Asegurar que el estudiante no cambie
                    informe_actualizado.estudiante = informe.estudiante
                    # ACTUALIZAR PROMEDIO (NUEVO)
                    informe_actualizado.promedio_progreso = promedio_progreso
                    informe_actualizado.sesiones_evaluadas = sesiones_evaluadas
                    informe_actualizado.save()
                    print("✅ Informe principal actualizado")
                    
                    # 2. Procesar las áreas de desarrollo (FALTABA ESTA PARTE)
                    print("=== PROCESANDO ÁREAS EN EDICIÓN ===")
                    areas_procesadas = 0
                    
                    for i in range(1, 8):  # Áreas del 1 al 7
                        evaluacion = request.POST.get(f'area_{i}')
                        recomendaciones = request.POST.get(f'recomendaciones_{i}', '')
                        
                        print(f"Área {i}: evaluacion='{evaluacion}', recomendaciones='{recomendaciones}'")
                        
                        if evaluacion:
                            try:
                                area = AreaDesarrollo.objects.get(id=i)
                                desarrollo_existente = desarrollos_dict.get(i)
                                
                                if desarrollo_existente:
                                    # Actualizar desarrollo existente
                                    desarrollo_existente.evaluacion = evaluacion
                                    desarrollo_existente.recomendaciones = recomendaciones
                                    desarrollo_existente.save()
                                    print(f"✅ Área {i} ACTUALIZADA: {evaluacion}")
                                else:
                                    # Crear nuevo desarrollo
                                    DesarrolloEducativo.objects.create(
                                        informe=informe,
                                        area=area,
                                        evaluacion=evaluacion,
                                        recomendaciones=recomendaciones
                                    )
                                    print(f"✅ Área {i} CREADA: {evaluacion}")
                                
                                areas_procesadas += 1
                                
                            except Exception as e:
                                print(f"❌ Error en área {i}: {e}")
                        else:
                            # Si no hay evaluación seleccionada, eliminar el desarrollo si existe
                            desarrollo_existente = desarrollos_dict.get(i)
                            if desarrollo_existente:
                                desarrollo_existente.delete()
                                print(f"🗑️ Área {i} ELIMINADA (sin evaluación)")
                    
                    print(f"=== EDICIÓN COMPLETADA: {areas_procesadas} áreas procesadas ===")
                    
                    messages.success(request, '✅ Informe final actualizado correctamente')
                    return redirect('registro_evolucion:ver_informe', pk=informe.pk)
                    
            except Exception as e:
                messages.error(request, f'❌ Error al actualizar informe: {str(e)}')
                print(f"❌ ERROR GENERAL EN EDICIÓN: {e}")
        else:
            messages.error(request, '❌ Por favor corrige los errores en el formulario')
            print(f"❌ ERRORES FORMULARIO EN EDICIÓN: {form.errors}")
    
    # CONTEXT siempre debe incluir 'form'
    context = {
        'form': form,
        'informe': informe,
        'desarrollos_dict': desarrollos_dict,
        'promedio_progreso': promedio_progreso,
        'sesiones_evaluadas': sesiones_evaluadas,
        'titulo': 'Editar Informe Final'
    }
    return render(request, 'registro_evolucion/editar_informe.html', context)

@login_required
def ver_informe_final(request, pk):
    """Ver detalle de informe final"""
    informe = get_object_or_404(InformeFinal, pk=pk)
    
    # Recuperar los desarrollos educativos ordenados por área
    desarrollos = informe.desarrollos.all().select_related('area').order_by('area__id')
    
    # Crear un diccionario para acceder fácilmente por área_id
    desarrollos_dict = {desarrollo.area_id: desarrollo for desarrollo in desarrollos}
    
    # Verificar si hay parámetro de éxito en la URL para mostrar el modal
    exito = request.GET.get('exito') == 'true'
    
    context = {
        'informe': informe,
        'desarrollos': desarrollos,
        'desarrollos_dict': desarrollos_dict,
        'exito': exito,  # Nuevo parámetro para el modal
    }
    return render(request, 'registro_evolucion/ver_informe.html', context)

@login_required
def generar_pdf_informe(request, pk):
    """Generar PDF del informe final"""
    try:
        informe = get_object_or_404(InformeFinal, pk=pk)
        desarrollos = informe.desarrollos.all().select_related('area').order_by('area__orden', 'area__id')
        
        # Función para convertir imágenes a base64
        def image_to_base64(image_path):
            try:
                with open(image_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                    if image_path.lower().endswith('.png'):
                        return f"data:image/png;base64,{encoded_string}"
                    elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
                        return f"data:image/jpeg;base64,{encoded_string}"
                    else:
                        return f"data:image/png;base64,{encoded_string}"
            except Exception as e:
                print(f"❌ Error cargando imagen {image_path}: {e}")
                return ""
        
        # Obtener rutas de las imágenes
        static_dir = os.path.join(settings.BASE_DIR, 'static')
        imagen_idai_path = os.path.join(static_dir, 'imagenes', 'idai.png')
        imagen_distrito_path = os.path.join(static_dir, 'imagenes', 'distrito.png')
        
        # Convertir imágenes a base64
        imagen_idai_b64 = image_to_base64(imagen_idai_path)
        imagen_distrito_b64 = image_to_base64(imagen_distrito_path)
        
        # Verificar si las imágenes se cargaron correctamente
        if not imagen_idai_b64:
            print("⚠️ No se pudo cargar la imagen idai.png")
        if not imagen_distrito_b64:
            print("⚠️ No se pudo cargar la imagen distrito.png")
        
        # Renderizar template a HTML
        html_string = render_to_string('registro_evolucion/pdf_informe.html', {
            'informe': informe,
            'desarrollos': desarrollos,
            'imagen_idai': imagen_idai_b64,
            'imagen_distrito': imagen_distrito_b64,
        })
        
        # Crear respuesta PDF
        response = HttpResponse(content_type='application/pdf')
        filename = f"informe_final_{informe.estudiante.documento_identidad}_{informe.gestion}.pdf"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        # Función callback para manejar recursos
        def link_callback(uri, rel):
            return uri
        
        # Generar PDF
        pisa_status = pisa.CreatePDF(
            html_string,
            dest=response,
            link_callback=link_callback
        )
        
        if pisa_status.err:
            print(f"❌ Error PDF: {pisa_status.err}")
            messages.error(request, '❌ Error al generar el PDF. Por favor intente nuevamente.')
            return redirect('registro_evolucion:ver_informe', pk=pk)
            
        return response
        
    except Exception as e:
        print(f"❌ Error inesperado al generar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'❌ Error inesperado al generar PDF: {str(e)}')
        return redirect('registro_evolucion:ver_informe', pk=pk)

@login_required
def eliminar_informe_final(request, pk):
    """Eliminar informe final"""
    informe = get_object_or_404(InformeFinal, pk=pk)
    
    if request.method == 'POST':
        informe.delete()
        messages.success(request, '✅ Informe final eliminado correctamente')
        return redirect('registro_evolucion:lista_informes')
    
    context = {
        'informe': informe
    }
    return render(request, 'registro_evolucion/confirmar_eliminar.html', context)

@login_required
def buscar_estudiante_ajax(request):
    """Búsqueda AJAX de estudiantes"""
    query = request.GET.get('q', '')
    
    if query:
        estudiantes = Estudiante.objects.filter(
            models.Q(nombres__icontains=query) |
            models.Q(apellido_paterno__icontains=query) |
            models.Q(apellido_materno__icontains=query) |
            models.Q(codigo_rude__icontains=query)
        )[:10]
        
        results = []
        for est in estudiantes:
            results.append({
                'id': est.id,
                'text': f"{est.nombres} {est.apellido_paterno} {est.apellido_materno} - RUDE: {est.codigo_rude}",
                'nombres': f"{est.nombres} {est.apellido_paterno} {est.apellido_materno}",
                'codigo_rude': est.codigo_rude,
                'fecha_nacimiento': est.fecha_nacimiento.strftime('%d/%m/%Y') if est.fecha_nacimiento else '',
                'edad': est.edad,
                'grado': f"{est.grado} {est.nivel}",
                'diagnostico': getattr(est, 'diagnostico', '')
            })
        
        return JsonResponse(results, safe=False)
    
    return JsonResponse([], safe=False)

@login_required
def cargar_areas_desarrollo(request):
    """Cargar áreas de desarrollo para AJAX"""
    areas = AreaDesarrollo.objects.filter(activo=True).order_by('orden')
    
    areas_data = []
    for area in areas:
        areas_data.append({
            'id': area.id,
            'nombre': area.nombre,
            'descripcion': area.descripcion
        })
    
    return JsonResponse(areas_data, safe=False)

@login_required

def crear_informe_desde_estudiante(request, estudiante_id):
    """Crear informe final para un estudiante específico - SIN RESTRICCIÓN DE SESIONES"""
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    
    # CALCULAR ESTADÍSTICAS (manejar casos donde no hay agenda)
    total_faltas = 0
    total_licencias = 0
    sesiones_completadas = 0
    
    if hasattr(estudiante, 'agenda'):
        total_faltas = estudiante.agenda.sesiones.filter(estado='ausente').count()
        total_licencias = estudiante.agenda.sesiones.filter(estado='justificada').count()
        sesiones_completadas = estudiante.agenda.sesiones_completadas
    
    # CALCULAR PROMEDIO DE PROGRESO
    try:
        if hasattr(estudiante, 'agenda'):
            sesiones_asistidas = estudiante.agenda.sesiones.filter(
                estado='asistio', 
                progreso__isnull=False
            ).exclude(progreso__exact=0)
            
            sesiones_evaluadas = sesiones_asistidas.count()
            if sesiones_evaluadas > 0:
                total_calificaciones = sum(sesion.progreso for sesion in sesiones_asistidas)
                promedio_progreso = total_calificaciones / sesiones_evaluadas
            else:
                promedio_progreso = 0.00
        else:
            promedio_progreso = 0.00
            sesiones_evaluadas = 0
    except Exception as e:
        print(f"Error calculando promedio: {e}")
        promedio_progreso = 0.00
        sesiones_evaluadas = 0
    
    # INICIALIZAR form
    form = InformeFinalForm(initial={
        'estudiante': estudiante,
        'gestion': '2025',
        'semestre_programa': 'PRIMER SEMESTRE',
        'diagnostico_educativo': getattr(estudiante, 'diagnostico', ''),
    })
    
    if request.method == 'POST':
        form = InformeFinalForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Guardar el informe principal
                    informe = form.save(commit=False)
                    informe.docente = request.user
                    informe.total_sesiones = 24
                    informe.sesiones_asistidas = sesiones_completadas
                    informe.total_faltas = total_faltas
                    informe.total_licencias = total_licencias
                    informe.promedio_progreso = promedio_progreso
                    informe.sesiones_evaluadas = sesiones_evaluadas
                    informe.save()
                    
                    print("=== INICIANDO GUARDADO DE ÁREAS ===")
                    
                    # 2. Guardar las áreas de desarrollo
                    areas_creadas = 0
                    for i in range(1, 8):
                        evaluacion = request.POST.get(f'area_{i}')
                        recomendaciones = request.POST.get(f'recomendaciones_{i}', '')
                        
                        print(f"Procesando área {i}: evaluacion='{evaluacion}', recomendaciones='{recomendaciones}'")
                        
                        if evaluacion:
                            try:
                                area = AreaDesarrollo.objects.get(id=i)
                                DesarrolloEducativo.objects.create(
                                    informe=informe,
                                    area=area,
                                    evaluacion=evaluacion,
                                    recomendaciones=recomendaciones
                                )
                                areas_creadas += 1
                                print(f"✅ Área {i} GUARDADA: {evaluacion}")
                            except Exception as e:
                                print(f"❌ Error guardando área {i}: {e}")
                        else:
                            print(f"⚠️ Área {i} sin evaluación seleccionada")
                    
                    print(f"=== RESULTADO: {areas_creadas}/7 áreas guardadas ===")
                    
                    # ✅ REDIRIGIR CON PARÁMETRO DE ÉXITO PARA MOSTRAR EL MODAL
                    messages.success(request, f'✅ Informe final creado correctamente con {areas_creadas} áreas de desarrollo')
                    url_ver_informe = reverse('registro_evolucion:ver_informe', kwargs={'pk': informe.pk})
                    return redirect(f"{url_ver_informe}?exito=true")
                    
            except Exception as e:
                messages.error(request, f'❌ Error al crear informe: {str(e)}')
                print(f"❌ ERROR GENERAL: {e}")
        else:
            messages.error(request, '❌ Por favor corrige los errores en el formulario')
            print(f"❌ ERRORES FORMULARIO: {form.errors}")
    
    context = {
        'form': form,
        'estudiante_seleccionado': estudiante,
        'total_faltas': total_faltas,
        'total_licencias': total_licencias,
        'promedio_progreso': promedio_progreso,
        'sesiones_evaluadas': sesiones_evaluadas,
        'sesiones_completadas': sesiones_completadas,
        'titulo': f'Nuevo Informe Final - {estudiante}'
    }
    return render(request, 'registro_evolucion/form_informe.html', context)