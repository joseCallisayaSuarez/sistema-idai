from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import EstudianteForm, TutorForm
from .models import Estudiante, Tutor
from django.http import HttpResponse
from django.template.loader import render_to_string

from io import BytesIO
import os
import base64
from django.conf import settings

# LISTA
def lista_estudiantes(request):
    estudiantes = Estudiante.objects.order_by('-created_at')
    return render(request, 'estudiantes/lista_estudiantes.html', {'estudiantes': estudiantes})

# REGISTRO
def registrar_estudiante(request):
    if request.method == 'POST':
        estudiante_form = EstudianteForm(request.POST, prefix='est')
        tutor_form = TutorForm(request.POST, prefix='tutor')
        if estudiante_form.is_valid() and tutor_form.is_valid():
            tutor = tutor_form.save()
            estudiante = estudiante_form.save(commit=False)
            estudiante.tutor = tutor
            estudiante.save()
            # Redirigir con parámetro para mostrar el modal
            return redirect(reverse('registrar_estudiante') + '?registro=exitoso')
    else:
        estudiante_form = EstudianteForm(prefix='est')
        tutor_form = TutorForm(prefix='tutor')

    return render(request, 'estudiantes/registrar_estudiante.html', {
        'estudiante_form': estudiante_form,
        'tutor_form': tutor_form
    })

# EDITAR
def editar_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    tutor = estudiante.tutor

    if request.method == 'POST':
        estudiante_form = EstudianteForm(request.POST, instance=estudiante, prefix='est')
        tutor_form = TutorForm(request.POST, instance=tutor, prefix='tutor')
        if estudiante_form.is_valid() and tutor_form.is_valid():
            tutor_form.save()
            estudiante_form.save()
            return redirect(reverse('lista_estudiantes'))
    else:
        estudiante_form = EstudianteForm(instance=estudiante, prefix='est')
        tutor_form = TutorForm(instance=tutor, prefix='tutor')

    return render(request, 'estudiantes/editar_estudiante.html', {
        'estudiante_form': estudiante_form,
        'tutor_form': tutor_form,
        'estudiante': estudiante
    })

# ELIMINAR
def eliminar_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    
    if request.method == 'POST':
        # Guardar los datos del estudiante antes de eliminarlo
        estudiante_data = {
            'nombres': estudiante.nombres,
            'apellido_paterno': estudiante.apellido_paterno,
            'documento_identidad': estudiante.documento_identidad
        }
        
        # Eliminar el estudiante
        estudiante.delete()
        
        # Renderizar la misma página con el modal de éxito
        return render(request, 'estudiantes/eliminar_estudiante.html', {
            'estudiante': estudiante_data,  # Pasamos los datos como diccionario
            'eliminado': True  # Flag para mostrar el modal
        })
    
    # GET request - mostrar formulario de confirmación
    return render(request, 'estudiantes/eliminar_estudiante.html', {
        'estudiante': estudiante,
        'eliminado': False
    })

def ver_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    return render(request, 'estudiantes/ver_estudiante.html', {'estudiante': estudiante})
#GENERAR PDF
# Agregar esta nueva función al final del archivo
# estudiantes/views.py - función simplificada sin imágenes
def generar_pdf_estudiantes(request):
    """Generar PDF de lista de estudiantes filtrados por semestre"""
    try:
        # Obtener parámetros de filtro
        semestre = request.GET.get('semestre', '')
        gestion = request.GET.get('gestion', '')
        
        # Filtrar estudiantes
        estudiantes = Estudiante.objects.all().order_by('apellido_paterno', 'nombres')
        
        if semestre:
            estudiantes = estudiantes.filter(semestre=semestre)
        if gestion:
            estudiantes = estudiantes.filter(gestion_ingreso=gestion)
        
        # Obtener descripciones para el título
        semestre_display = ""
        if semestre == '1':
            semestre_display = "Primer Semestre"
        elif semestre == '2':
            semestre_display = "Segundo Semestre"
        
        # Renderizar template a HTML SIN IMÁGENES
        html_string = render_to_string('estudiantes/pdf_lista_estudiantes.html', {
            'estudiantes': estudiantes,
            'semestre': semestre,
            'semestre_display': semestre_display,
            'gestion': gestion,
            'total_estudiantes': estudiantes.count(),
        })
        
        # Crear respuesta PDF
        response = HttpResponse(content_type='application/pdf')
        
        # Nombre del archivo según los filtros
        if semestre and gestion:
            filename = f"lista_estudiantes_semestre_{semestre}_gestion_{gestion}.pdf"
        elif semestre:
            filename = f"lista_estudiantes_semestre_{semestre}.pdf"
        elif gestion:
            filename = f"lista_estudiantes_gestion_{gestion}.pdf"
        else:
            filename = "lista_estudiantes_completa.pdf"
            
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        # Generar PDF con mejor manejo de errores
        pisa_status = pisa.CreatePDF(
            html_string,
            dest=response,
            encoding='UTF-8'
        )
        
        if pisa_status.err:
            print(f"❌ Error PDF: {pisa_status.err}")
            # Devolver el HTML para debug
            return HttpResponse(html_string, content_type='text/html')
            
        return response
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error inesperado: {str(e)}")
