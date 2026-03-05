import os
import json
from datetime import datetime, date, time
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction
from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone
from .models import Backup

# ============================================
# FUNCIONES AUXILIARES PARA JSON
# ============================================

def json_serializer(obj):
    """Serializer personalizado para objetos Python no serializables por defecto"""
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    raise TypeError(f"Type {type(obj)} not serializable")

def limpiar_datos_json(datos):
    """Limpia recursivamente un diccionario para hacerlo JSON serializable - VERSIÓN MEJORADA"""
    
    # Si es un objeto de modelo Django, convertir a diccionario simple
    if hasattr(datos, '_meta'):  # Es un modelo Django
        return {
            'model': f"{datos._meta.app_label}.{datos._meta.model_name}",
            'id': datos.id,
            'repr': str(datos)
        }
    
    if isinstance(datos, dict):
        return {k: limpiar_datos_json(v) for k, v in datos.items()}
    elif isinstance(datos, list):
        return [limpiar_datos_json(item) for item in datos]
    elif isinstance(datos, (datetime, date, time, Decimal)):
        return json_serializer(datos)
    elif isinstance(datos, (int, float, str, bool, type(None))):
        return datos
    else:
        try:
            # Intentar serializar directamente
            json.dumps(datos, default=str)
            return datos
        except (TypeError, ValueError):
            # Si falla, convertir a string
            return str(datos)

def convertir_fecha(fecha_str):
    """Convierte string a fecha - maneja múltiples formatos"""
    from datetime import datetime, date
    
    if not fecha_str:
        return None
    
    try:
        # Si ya es un objeto date
        if isinstance(fecha_str, (date, datetime)):
            if isinstance(fecha_str, datetime):
                return fecha_str.date()
            return fecha_str
        
        # Si es string, intentar diferentes formatos
        if isinstance(fecha_str, str):
            # Formato ISO con T (datetime)
            if 'T' in fecha_str:
                if fecha_str.endswith('Z'):
                    return datetime.fromisoformat(fecha_str.replace('Z', '+00:00')).date()
                return datetime.fromisoformat(fecha_str).date()
            
            # Formato date ISO (YYYY-MM-DD)
            elif len(fecha_str) == 10 and fecha_str.count('-') == 2:
                try:
                    return datetime.strptime(fecha_str, '%Y-%m-%d').date()
                except:
                    # Intentar formato DD/MM/YYYY
                    return datetime.strptime(fecha_str, '%d/%m/%Y').date()
            
            # Otros formatos comunes
            elif '/' in fecha_str:
                # DD/MM/YYYY
                if len(fecha_str) == 10:
                    return datetime.strptime(fecha_str, '%d/%m/%Y').date()
                # DD/MM/YY
                elif len(fecha_str) == 8:
                    return datetime.strptime(fecha_str, '%d/%m/%y').date()
    except Exception as e:
        print(f"⚠️ Error convirtiendo fecha '{fecha_str}': {str(e)}")
    
    return None

# ============================================
# VISTAS PRINCIPALES
# ============================================

@login_required
def dashboard(request):
    """Dashboard principal de backups"""
    backups = Backup.objects.all().order_by('-fecha_creacion')
    
    # Estadísticas
    total_backups = backups.count()
    backups_completados = backups.filter(estado='completado')
    tamano_total = sum(b.tamano for b in backups_completados)
    
    context = {
        'backups': backups,
        'total_backups': total_backups,
        'tamano_total': tamano_total,
        'backups_completados': backups_completados.count(),
        'fecha_actual': timezone.now(),
    }
    
    return render(request, 'backups/dashboard.html', context)

@login_required
@require_POST
def crear_backup(request):
    """Crea un nuevo backup y lo descarga"""
    nombre = request.POST.get('nombre', '').strip()
    descripcion = request.POST.get('descripcion', '').strip()
    
    if not nombre:
        messages.error(request, '❌ El nombre del backup es requerido')
        return redirect('backups:dashboard')
    
    try:
        # Crear backup en la base de datos
        backup = Backup.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            usuario=request.user,
            estado='en_progreso'
        )
        
        # Ejecutar comando para crear backup real
        call_command('crear_backup', usuario_id=request.user.id, nombre=nombre)
        
        # Refrescar el objeto
        backup.refresh_from_db()
        
        if backup.estado == 'completado' and backup.archivo:
            # Preparar respuesta para descargar archivo
            response = HttpResponse(backup.archivo.read(), content_type='application/json')
            filename = f"backup_{backup.id}_{request.user.username}.json"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            messages.success(request, '✅ Backup creado exitosamente')
            return response
        else:
            messages.error(request, f'❌ Backup no se completó. Estado: {backup.estado}')
            
    except Exception as e:
        messages.error(request, f'❌ Error al crear backup: {str(e)}')
    
    return redirect('backups:dashboard')

@login_required
def descargar_backup(request, backup_id):
    """Descarga un backup existente"""
    backup = get_object_or_404(Backup, id=backup_id, estado='completado')
    
    if backup.archivo and backup.archivo.storage.exists(backup.archivo.name):
        response = HttpResponse(backup.archivo.read(), content_type='application/json')
        filename = f"backup_{backup.id}_{backup.usuario.username if backup.usuario else 'sistema'}.json"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    messages.error(request, '❌ El archivo de backup no existe')
    return redirect('backups:dashboard')

@login_required
@require_POST
def restaurar_backup(request):
    """RESTAURA el sistema desde un archivo de backup"""
    
    print("🔍 DEBUG: Función restaurar_backup llamada")
    
    # Obtener datos del formulario
    archivo = request.FILES.get('archivo_backup')
    tipo_restauracion = request.POST.get('tipo_restauracion', 'completa')
    confirmar = request.POST.get('confirmar')
    confirmacion_extra = request.POST.get('confirmacion_extra')
    confirmar_final = request.POST.get('confirmar_final')
    
    print(f"  - Archivo recibido: {'SÍ' if archivo else 'NO'}")
    print(f"  - Tipo restauración: {tipo_restauracion}")
    print(f"  - Confirmar: {confirmar}")
    print(f"  - Confirmación extra: {confirmacion_extra}")
    print(f"  - Confirmar final: {confirmar_final}")
    
    # PRIMERA ETAPA: Subir archivo y mostrar preview
    if archivo and not confirmacion_extra:
        try:
            # 1. Leer el archivo JSON
            print("  - Leyendo archivo JSON...")
            contenido = archivo.read().decode('utf-8')
            datos_backup = json.loads(contenido)
            
            # 2. Validar estructura
            if not isinstance(datos_backup, dict) or 'datos' not in datos_backup:
                raise ValueError("Archivo de backup inválido")
            
            print(f"  - Apps en backup: {list(datos_backup.get('datos', {}).keys())}")
            
            # 3. GUARDAR DATOS EN SESIÓN para la próxima etapa
            request.session['backup_data'] = contenido  # Guardar como string
            request.session['backup_filename'] = archivo.name
            request.session['backup_tipo'] = tipo_restauracion
            
            # 4. Mostrar preview
            print("🔍 Mostrando preview de restauración")
            return mostrar_preview_restauracion(request, datos_backup, archivo.name, tipo_restauracion)
            
        except json.JSONDecodeError:
            messages.error(request, '❌ El archivo no es un JSON válido')
            print("❌ Error: JSON inválido")
            return redirect('backups:dashboard')
        except Exception as e:
            messages.error(request, f'❌ Error al procesar el archivo: {str(e)}')
            print(f"❌ Error: {str(e)}")
            return redirect('backups:dashboard')
    
    # SEGUNDA ETAPA: Confirmación y ejecución
    elif confirmacion_extra == 'si':
        # Verificar confirmación final
        if not confirmar_final:
            messages.error(request, '❌ Debes marcar la casilla de confirmación final')
            return redirect('backups:dashboard')
        
        # Recuperar datos de la sesión
        contenido = request.session.get('backup_data')
        archivo_name = request.session.get('backup_filename')
        tipo_restauracion = request.session.get('backup_tipo', 'completa')
        
        if not contenido:
            messages.error(request, '❌ Sesión de restauración expirada. Sube el archivo nuevamente.')
            return redirect('backups:dashboard')
        
        try:
            # Convertir string de vuelta a JSON
            datos_backup = json.loads(contenido)
            
            # Ejecutar restauración real
            return ejecutar_restauracion_real(request, datos_backup, tipo_restauracion, archivo_name)
            
        except Exception as e:
            messages.error(request, f'❌ Error al restaurar: {str(e)}')
            print(f"❌ Error en restauración: {str(e)}")
            return redirect('backups:dashboard')
    
    # Si no hay archivo y no es confirmación, error
    else:
        messages.error(request, '❌ Debes seleccionar un archivo de backup')
        return redirect('backups:dashboard')

def mostrar_preview_restauracion(request, datos_backup, nombre_archivo, tipo_restauracion):
    """Muestra vista previa antes de restaurar - VERSIÓN MEJORADA"""
    
    print("🔍 Mostrando preview de restauración MEJORADO")
    
    # 1. Preparar detalles del backup (como espera el template)
    detalles = {}
    total_registros = 0
    total_apps = len(datos_backup.get('datos', {}))
    
    for app_label, app_data in datos_backup.get('datos', {}).items():
        detalles[app_label] = {}
        for model_name, info in app_data.items():
            if 'count' in info:
                detalles[app_label][model_name] = info['count']
                total_registros += info['count']
    
    # 2. Obtener datos actuales del sistema para comparar
    datos_actuales = obtener_datos_actuales_sistema(list(datos_backup.get('datos', {}).keys()))
    
    # 3. Preparar resumen del backup
    resumen_backup = {}
    for app_label, app_data in datos_backup.get('datos', {}).items():
        modelos = []
        total_app_registros = 0
        
        for model_name, info in app_data.items():
            if 'count' in info:
                modelos.append({
                    'nombre': model_name,
                    'count': info['count']
                })
                total_app_registros += info['count']
        
        resumen_backup[app_label] = {
            'modelos': len(modelos),
            'registros': total_app_registros,
            'detalle': modelos[:5]  # Solo primeros 5 para el preview
        }
    
    # 4. Contexto completo para el template
    context = {
        'nombre_archivo': nombre_archivo,
        'tipo_restauracion': tipo_restauracion,
        
        # Para template preview_restauracion.html (el que estás usando)
        'detalles': detalles,  # <-- IMPORTANTE
        'total_registros': total_registros,
        'total_apps': total_apps,
        
        # Para template comparativo (si usas el otro)
        'resumen_backup': resumen_backup,
        'total_apps_backup': len(resumen_backup),
        'total_registros_backup': total_registros,
        'datos_actuales': datos_actuales,
    }
    
    return render(request, 'backups/preview_restauracion.html', context)

def obtener_datos_actuales_sistema(apps_backup):
    """Obtiene datos actuales del sistema para comparar"""
    datos_actuales = {}
    
    try:
        # Agenda
        if 'agenda' in apps_backup:
            from agenda.models import AgendaEstudiante, Sesion
            datos_actuales['agenda'] = {
                'modelos': 2,
                'registros': AgendaEstudiante.objects.count() + Sesion.objects.count(),
                'detalle': [
                    {'nombre': 'AgendaEstudiante', 'count': AgendaEstudiante.objects.count()},
                    {'nombre': 'Sesion', 'count': Sesion.objects.count()}
                ],
                'error': None
            }
        
        # Estudiantes
        if 'estudiantes' in apps_backup:
            from estudiantes.models import Estudiante
            datos_actuales['estudiantes'] = {
                'modelos': 1,
                'registros': Estudiante.objects.count(),
                'detalle': [
                    {'nombre': 'Estudiante', 'count': Estudiante.objects.count()}
                ],
                'error': None
            }
        
        # Usuarios
        if 'usuarios' in apps_backup:
            from django.contrib.auth.models import User
            datos_actuales['usuarios'] = {
                'modelos': 1,
                'registros': User.objects.count(),
                'detalle': [
                    {'nombre': 'User', 'count': User.objects.count()}
                ],
                'error': None
            }
            
    except Exception as e:
        # Si hay error, registrar pero continuar
        datos_actuales['error'] = f"No se pudieron obtener datos actuales: {str(e)}"
    
    return datos_actuales

def ejecutar_restauracion_real(request, datos_backup, tipo_restauracion, nombre_archivo):
    """Ejecuta la restauración REAL - VERSIÓN CORREGIDA Y COMPLETA"""
    
    print("🚀 EJECUTANDO RESTAURACIÓN REAL - VERSIÓN FINAL")
    
    try:
        with transaction.atomic():
            estadisticas = {
                'registros_creados': 0,
                'registros_actualizados': 0,
                'errores': []
            }
            
            # Diccionarios para mapear IDs a instancias
            tutores_dict = {}
            estudiantes_dict = {}
            agendas_dict = {}
            
            # ====================================
            # 1. RESTAURAR TUTORES PRIMERO
            # ====================================
            if 'tutores' in datos_backup.get('datos', {}):
                print("👨‍👩‍👧‍👦 Restaurando tutores...")
                tutores_data = datos_backup['datos']['tutores']
                
                from estudiantes.models import Tutor
                
                if 'tutor' in tutores_data:
                    info = tutores_data['tutor']
                    if 'objetos' in info:
                        print(f"  - Procesando {len(info['objetos'])} tutores...")
                        
                        for obj_data in info['objetos']:
                            try:
                                pk = obj_data.get('pk')
                                fields = obj_data.get('fields', {})
                                
                                # Convertir campos especiales
                                fields = convertir_campos_desde_json(fields)
                                
                                # Crear o actualizar tutor
                                obj, created = Tutor.objects.update_or_create(
                                    id=pk,
                                    defaults=fields
                                )
                                
                                tutores_dict[pk] = obj
                                
                                if created:
                                    estadisticas['registros_creados'] += 1
                                    print(f"  ✅ Tutor {pk}: {obj.nombres} CREADO")
                                else:
                                    estadisticas['registros_actualizados'] += 1
                                    print(f"  🔄 Tutor {pk}: {obj.nombres} ACTUALIZADO")
                                
                            except Exception as e:
                                error_msg = f"Error tutor {obj_data.get('pk')}: {str(e)}"
                                estadisticas['errores'].append(error_msg)
                                print(f"  ❌ {error_msg}")
            
            # ====================================
            # 2. CREAR TUTOR POR DEFECTO SI NO HAY TUTORES
            # ====================================
            from estudiantes.models import Tutor, Estudiante
            
            if not tutores_dict:
                print("👨‍👩‍👧‍👦 No hay tutores en backup, creando tutor por defecto...")
                tutor_por_defecto, created = Tutor.objects.get_or_create(
                    nombres="Tutor Backup",
                    apellido_paterno="Temporal",
                    defaults={
                        'apellido_materno': 'Backup',
                        'ci': '0000000',
                        'telefono': '000-000-0000',
                        'celular': '000-000-0000',
                        'ocupacion': 'Temporal',
                        'parentesco': 'Temporal',
                        'zona': 'Sin especificar',
                        'avenida': 'Sin especificar',
                        'nro_vivienda': '0'
                    }
                )
                
                tutores_dict[tutor_por_defecto.id] = tutor_por_defecto
                
                if created:
                    estadisticas['registros_creados'] += 1
                    print(f"  ✅ Creado tutor por defecto ID: {tutor_por_defecto.id}")
                else:
                    print(f"  🔄 Usando tutor por defecto existente ID: {tutor_por_defecto.id}")
            
            # ====================================
            # 3. RESTAURAR ESTUDIANTES
            # ====================================
            if 'estudiantes' in datos_backup.get('datos', {}):
                print("👥 RESTAURANDO ESTUDIANTES...")
                estudiantes_data = datos_backup['datos']['estudiantes']
                
                if tipo_restauracion == 'completa':
                    print("  - Limpiando estudiantes existentes...")
                    Estudiante.objects.all().delete()
                
                if 'estudiante' in estudiantes_data:
                    info = estudiantes_data['estudiante']
                    if 'objetos' in info:
                        print(f"  - Procesando {len(info['objetos'])} estudiantes...")
                        
                        for obj_data in info['objetos']:
                            try:
                                pk = obj_data.get('pk')
                                fields = obj_data.get('fields', {})
                                
                                # Convertir campos especiales
                                fields = convertir_campos_desde_json(fields)
                                
                                # Obtener tutor (instancia)
                                tutor_id = fields.get('tutor')
                                if tutor_id and tutor_id in tutores_dict:
                                    fields['tutor'] = tutores_dict[tutor_id]
                                else:
                                    # Usar el primer tutor disponible
                                    primer_tutor = list(tutores_dict.values())[0]
                                    fields['tutor'] = primer_tutor
                                    print(f"  ⚠️ Estudiante {pk} sin tutor válido, asignando tutor: {primer_tutor.nombres}")
                                
                                # Remover tutor_id si existe
                                if 'tutor_id' in fields:
                                    del fields['tutor_id']
                                
                                # Manejar campos JSON
                                for json_field in ['resultados_evaluacion', 'programa_apoyo']:
                                    if json_field in fields and isinstance(fields[json_field], str):
                                        try:
                                            fields[json_field] = json.loads(fields[json_field])
                                        except:
                                            fields[json_field] = []
                                
                                # Crear/actualizar estudiante
                                obj, created = Estudiante.objects.update_or_create(
                                    id=pk,
                                    defaults=fields
                                )
                                
                                estudiantes_dict[pk] = obj
                                
                                if created:
                                    estadisticas['registros_creados'] += 1
                                    print(f"  ✅ Estudiante {pk}: {obj.nombres} CREADO")
                                else:
                                    estadisticas['registros_actualizados'] += 1
                                    print(f"  🔄 Estudiante {pk}: {obj.nombres} ACTUALIZADO")
                                
                            except Exception as e:
                                error_msg = f"Error estudiante {obj_data.get('pk')}: {str(e)}"
                                estadisticas['errores'].append(error_msg)
                                print(f"  ❌ {error_msg}")
            
            # ====================================
            # 4. VERIFICAR QUE HAYA ESTUDIANTES
            # ====================================
            total_estudiantes = Estudiante.objects.count()
            print(f"👥 TOTAL ESTUDIANTES EN BD: {total_estudiantes}")
            
            if total_estudiantes == 0:
                print("⚠️  CRÍTICO: No hay estudiantes en la base de datos")
                messages.warning(request, "⚠️ No se pudieron crear estudiantes del backup")
            
            # ====================================
            # 5. RESTAURAR AGENDAS (DIAGNÓSTICO DETALLADO)
            # ====================================
            agendas_creadas = 0
            agendas_omitidas = 0
            sesiones_creadas = 0
            sesiones_omitidas = 0
            
            if 'agenda' in datos_backup.get('datos', {}) and estudiantes_dict:
                print("📅 Restaurando agendas...")
                agenda_data = datos_backup['datos']['agenda']
                
                from agenda.models import AgendaEstudiante, Sesion
                
                if tipo_restauracion == 'completa':
                    print("  - Limpiando agendas existentes...")
                    AgendaEstudiante.objects.all().delete()
                    Sesion.objects.all().delete()
                
                # Restaurar AgendaEstudiante - DIAGNÓSTICO MEJORADO
                if 'agendaestudiante' in agenda_data:
                    info = agenda_data['agendaestudiante']
                    if 'objetos' in info:
                        print(f"🔍 DIAGNÓSTICO AGENDAS: {len(info['objetos'])} agendas en backup")
                        
                        # Mostrar primera agenda para diagnóstico
                        if info['objetos']:
                            primera_agenda = info['objetos'][0]
                            print(f"  📋 Primer agenda PK: {primera_agenda.get('pk')}")
                            print(f"  📋 Campos: {list(primera_agenda.get('fields', {}).keys())}")
                            print(f"  📋 Estudiante ID en agenda: {primera_agenda['fields'].get('estudiante')}")
                            print(f"  📋 Estudiantes disponibles: {list(estudiantes_dict.keys())[:5]}...")
                        
                        for obj_data in info['objetos']:
                            try:
                                pk = obj_data.get('pk')
                                fields = obj_data.get('fields', {})
                                
                                # Convertir campos
                                fields = convertir_campos_desde_json(fields)
                                
                                estudiante_id = fields.get('estudiante')
                                
                                # VERIFICAR SI EL ESTUDIANTE EXISTE
                                if estudiante_id not in estudiantes_dict:
                                    print(f"  ❗ Estudiante {estudiante_id} NO ENCONTRADO para agenda {pk}")
                                    print(f"     Estudiantes disponibles: {list(estudiantes_dict.keys())}")
                                    agendas_omitidas += 1
                                    continue
                                
                                # Obtener instancia del estudiante
                                fields['estudiante'] = estudiantes_dict[estudiante_id]
                                
                                # Crear agenda
                                agenda, created = AgendaEstudiante.objects.update_or_create(
                                    id=pk,
                                    defaults=fields
                                )
                                
                                agendas_dict[pk] = agenda
                                
                                if created:
                                    estadisticas['registros_creados'] += 1
                                    agendas_creadas += 1
                                    print(f"  ✅ Agenda {pk} CREADA para estudiante {estudiante_id}")
                                else:
                                    estadisticas['registros_actualizados'] += 1
                                    print(f"  🔄 Agenda {pk} actualizada para estudiante {estudiante_id}")
                                
                            except Exception as e:
                                error_msg = f"Error agenda {obj_data.get('pk')}: {str(e)}"
                                estadisticas['errores'].append(error_msg)
                                print(f"  ❌ {error_msg}")
                        
                        print(f"  📊 RESUMEN AGENDAS: {agendas_creadas} creadas, {agendas_omitidas} omitidas")
                        print(f"  📊 Agendas en dict: {list(agendas_dict.keys())}")
                
                # Restaurar Sesiones - SOLO SI HAY AGENDAS
                if 'sesion' in agenda_data and agendas_dict:
                    info = agenda_data['sesion']
                    if 'objetos' in info:
                        print(f"  - Procesando {len(info['objetos'])} sesiones...")
                        
                        for obj_data in info['objetos']:
                            try:
                                pk = obj_data.get('pk')
                                fields = obj_data.get('fields', {})
                                
                                # Convertir campos
                                fields = convertir_campos_desde_json(fields)
                                
                                # Verificar que la agenda existe
                                agenda_id = fields.get('agenda')
                                if agenda_id not in agendas_dict:
                                    # Verificar si existe en la BD
                                    try:
                                        agenda = AgendaEstudiante.objects.get(id=agenda_id)
                                        agendas_dict[agenda_id] = agenda
                                        print(f"  🔍 Agenda {agenda_id} encontrada en BD")
                                    except AgendaEstudiante.DoesNotExist:
                                        print(f"  ⚠️ Agenda {agenda_id} no existe para sesión {pk}, omitiendo...")
                                        sesiones_omitidas += 1
                                        continue
                                
                                # Obtener instancia de la agenda
                                fields['agenda'] = agendas_dict[agenda_id]
                                
                                # Crear o actualizar sesión
                                obj, created = Sesion.objects.update_or_create(
                                    id=pk,
                                    defaults=fields
                                )
                                
                                if created:
                                    estadisticas['registros_creados'] += 1
                                    sesiones_creadas += 1
                                    print(f"  ✅ Sesión {pk} CREADA para agenda {agenda_id}")
                                else:
                                    estadisticas['registros_actualizados'] += 1
                                    print(f"  🔄 Sesión {pk} actualizada para agenda {agenda_id}")
                                
                            except Exception as e:
                                error_msg = f"Error sesión {obj_data.get('pk')}: {str(e)}"
                                estadisticas['errores'].append(error_msg)
                                print(f"  ❌ {error_msg}")
                        
                        print(f"  📊 RESUMEN SESIONES: {sesiones_creadas} creadas, {sesiones_omitidas} omitidas")
            
            # ====================================
            # 6. RESTAURAR REGISTRO EVOLUCIÓN (CORREGIDO)
            # ====================================
            if 'registro_evolucion' in datos_backup.get('datos', {}) and estudiantes_dict:
                print("📝 Restaurando registro de evolución...")
                registro_data = datos_backup['datos']['registro_evolucion']
                
                from registro_evolucion.models import InformeFinal
                
                # Restaurar InformeFinal
                if 'informefinal' in registro_data:
                    info = registro_data['informefinal']
                    if 'objetos' in info:
                        print(f"  - Procesando {len(info['objetos'])} informes finales...")
                        
                        for obj_data in info['objetos']:
                            try:
                                pk = obj_data.get('pk')
                                fields = obj_data.get('fields', {})
                                
                                # Convertir campos
                                fields = convertir_campos_desde_json(fields)
                                
                                # Verificar que el estudiante existe
                                estudiante_id = fields.get('estudiante')
                                if estudiante_id not in estudiantes_dict:
                                    print(f"  ⚠️ Estudiante {estudiante_id} no existe para informe {pk}, omitiendo...")
                                    continue
                                
                                # Obtener instancia del estudiante
                                fields['estudiante'] = estudiantes_dict[estudiante_id]
                                
                                # Manejar campo docente (usuario)
                                docente_id = fields.get('docente')
                                if docente_id:
                                    from usuarios.models import Usuario
                                    try:
                                        fields['docente'] = Usuario.objects.get(id=docente_id)
                                    except Usuario.DoesNotExist:
                                        print(f"  ⚠️ Docente {docente_id} no existe para informe {pk}, usando usuario actual")
                                        fields['docente'] = request.user
                                
                                # Crear o actualizar informe
                                obj, created = InformeFinal.objects.update_or_create(
                                    id=pk,
                                    defaults=fields
                                )
                                
                                if created:
                                    estadisticas['registros_creados'] += 1
                                    print(f"  ✅ Informe Final {pk} CREADO para estudiante {estudiante_id}")
                                else:
                                    estadisticas['registros_actualizados'] += 1
                                    print(f"  🔄 Informe Final {pk} ACTUALIZADO para estudiante {estudiante_id}")
                                
                            except Exception as e:
                                error_msg = f"Error informe final {obj_data.get('pk')}: {str(e)}"
                                estadisticas['errores'].append(error_msg)
                                print(f"  ❌ {error_msg}")
            
            # ====================================
            # 7. CREAR REGISTRO DE RESTAURACIÓN (VERSIÓN SIMPLIFICADA)
            # ====================================
            
            # En lugar de guardar todo el backup, guardar solo un resumen
            resumen_restauracion = {
                'nombre_archivo': nombre_archivo,
                'tipo_restauracion': tipo_restauracion,
                'fecha': timezone.now().isoformat(),
                'estadisticas': {
                    'estudiantes': total_estudiantes,
                    'agendas': agendas_creadas,
                    'sesiones': sesiones_creadas,
                    'registros_creados': estadisticas['registros_creados'],
                    'registros_actualizados': estadisticas['registros_actualizados'],
                    'errores': len(estadisticas['errores'])
                },
                'usuario': request.user.username
            }
            
            # Crear registro de restauración
            Backup.objects.create(
                nombre=f"RESTAURADO: {nombre_archivo}",
                descripcion=f"Restauración {tipo_restauracion} - {total_estudiantes} estudiantes, {agendas_creadas} agendas, {sesiones_creadas} sesiones",
                usuario=request.user,
                estado='completado',
                datos_json=resumen_restauracion  # Guardar solo el resumen, no todo el backup
            )
            
            # Limpiar sesión
            for key in ['backup_data', 'backup_filename', 'backup_tipo']:
                if key in request.session:
                    del request.session[key]
            
            # ====================================
            # 8. MOSTRAR RESULTADOS FINALES
            # ====================================
            print(f"✅ RESTAURACIÓN COMPLETADA EXITOSAMENTE")
            print(f"   - Estudiantes: {total_estudiantes}")
            print(f"   - Agendas creadas: {agendas_creadas}")
            print(f"   - Sesiones creadas: {sesiones_creadas}")
            print(f"   - Registros creados: {estadisticas['registros_creados']}")
            print(f"   - Registros actualizados: {estadisticas['registros_actualizados']}")
            
            # Mensajes al usuario
            messages.success(request, f"✅ Restauración completada exitosamente")
            
            if total_estudiantes > 0:
                messages.info(request, f"👥 {total_estudiantes} estudiantes restaurados")
            
            if agendas_creadas > 0:
                messages.info(request, f"📅 {agendas_creadas} agendas restauradas")
            else:
                messages.warning(request, f"⚠️ No se pudieron restaurar agendas - verifica los IDs de estudiantes en las agendas")
            
            if sesiones_creadas > 0:
                messages.info(request, f"📋 {sesiones_creadas} sesiones creadas")
            
            if estadisticas['errores']:
                messages.warning(request, f"⚠️ {len(estadisticas['errores'])} errores encontrados")
                # Mostrar primeros 3 errores
                for error in estadisticas['errores'][:3]:
                    print(f"  ❗ Error: {error}")
            
            return redirect('backups:dashboard')
            
    except Exception as e:
        print(f"💥 ERROR CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        
        messages.error(request, f'❌ Error crítico en restauración: {str(e)}')
        return redirect('backups:dashboard')

# ============================================
# FUNCIONES DE RESTAURACIÓN INDIVIDUAL
# ============================================

def restaurar_tutor_individual(obj_data, estadisticas):
    """Restaura un tutor individual"""
    from estudiantes.models import Tutor
    
    pk = obj_data.get('pk')
    fields = obj_data.get('fields', {})
    
    # Convertir campos especiales
    fields = convertir_campos_desde_json(fields)
    
    # Crear o actualizar tutor
    obj, created = Tutor.objects.update_or_create(
        id=pk,
        defaults=fields
    )
    
    if created:
        estadisticas['registros_creados'] += 1
    else:
        estadisticas['registros_actualizados'] += 1
    
    return obj

def restaurar_usuario_individual(obj_data, estadisticas, usuario_actual):
    """Restaura un usuario individual"""
    from django.contrib.auth.models import User
    
    pk = obj_data.get('pk')
    fields = obj_data.get('fields', {})
    
    # No restaurar el usuario actual
    if pk == usuario_actual.id:
        print(f"⚠️ Saltando usuario actual (ID: {pk})")
        return None
    
    # Verificar si usuario ya existe
    try:
        usuario = User.objects.get(id=pk)
        # Actualizar campos excepto password
        for key, value in fields.items():
            if key != 'password':
                setattr(usuario, key, value)
        usuario.save()
        estadisticas['registros_actualizados'] += 1
    except User.DoesNotExist:
        # Crear nuevo usuario
        usuario = User.objects.create(
            id=pk,
            username=fields.get('username', f'usuario_{pk}'),
            email=fields.get('email', ''),
            first_name=fields.get('first_name', ''),
            last_name=fields.get('last_name', ''),
            is_active=fields.get('is_active', True),
            is_staff=fields.get('is_staff', False),
            is_superuser=fields.get('is_superuser', False),
        )
        usuario.set_password('password_temporal')
        usuario.save()
        estadisticas['registros_creados'] += 1
    
    return usuario

def restaurar_estudiante_individual(obj_data, estadisticas, tutores_ids, tutor_por_defecto_id):
    """Restaura un estudiante individual - VERSIÓN ROBUSTA"""
    from estudiantes.models import Estudiante, Tutor
    
    pk = obj_data.get('pk')
    fields = obj_data.get('fields', {})
    
    # Convertir campos especiales
    fields = convertir_campos_desde_json(fields)
    
    # Manejar relación con tutor - SIEMPRE asignar un tutor válido
    tutor_id = fields.get('tutor')
    
    # Verificar si el tutor existe
    if tutor_id:
        # Verificar si el tutor está en los IDs restaurados
        if tutor_id in tutores_ids:
            # El tutor fue restaurado en esta sesión
            tutor_valido = tutor_id
        else:
            # Verificar si existe en la base de datos
            if Tutor.objects.filter(id=tutor_id).exists():
                tutor_valido = tutor_id
                tutores_ids.add(tutor_id)  # Agregar a la lista
            else:
                print(f"⚠️ Tutor {tutor_id} no existe para estudiante {pk}, usando tutor por defecto")
                tutor_valido = tutor_por_defecto_id
    else:
        # Si no tiene tutor en el backup, usar tutor por defecto
        tutor_valido = tutor_por_defecto_id
    
    # Asegurar que siempre haya un tutor válido
    fields['tutor'] = tutor_valido
    
    # Crear o actualizar estudiante
    try:
        obj, created = Estudiante.objects.update_or_create(
            id=pk,
            defaults=fields
        )
        
        if created:
            estadisticas['registros_creados'] += 1
        else:
            estadisticas['registros_actualizados'] += 1
        
        print(f"  ✓ Estudiante {pk} creado/actualizado")
        return obj
    except Exception as e:
        print(f"❌ Error en estudiante {pk}: {str(e)}")
        
        # Intentar con valores mínimos si falla
        try:
            print(f"  🔄 Reintentando estudiante {pk} con valores básicos...")
            
            # Campos mínimos requeridos para Estudiante
            campos_minimos = {
                'nombres': fields.get('nombres', 'Estudiante'),
                'apellido_paterno': fields.get('apellido_paterno', 'Backup'),
                'tutor': tutor_valido  # SIEMPRE incluir tutor
            }
            
            # Agregar otros campos si están disponibles
            if 'apellido_materno' in fields:
                campos_minimos['apellido_materno'] = fields['apellido_materno']
            if 'fecha_nacimiento' in fields:
                campos_minimos['fecha_nacimiento'] = fields['fecha_nacimiento']
            if 'ci' in fields:
                campos_minimos['ci'] = fields['ci']
            
            obj, created = Estudiante.objects.update_or_create(
                id=pk,
                defaults=campos_minimos
            )
            
            if created:
                estadisticas['registros_creados'] += 1
            else:
                estadisticas['registros_actualizados'] += 1
            
            print(f"  ✓ Estudiante {pk} restaurado con valores básicos")
            return obj
        except Exception as e2:
            print(f"  ❌ Fallo definitivo en estudiante {pk}: {str(e2)}")
            return None

def restaurar_agenda_individual(obj_data, estadisticas, estudiantes_ids):
    """Restaura una agenda individual"""
    from agenda.models import AgendaEstudiante
    from estudiantes.models import Estudiante
    
    pk = obj_data.get('pk')
    fields = obj_data.get('fields', {})
    
    fields = convertir_campos_desde_json(fields)
    
    # Verificar que el estudiante existe
    estudiante_id = fields.get('estudiante')
    
    if not estudiante_id:
        print(f"⚠️ Agenda {pk} no tiene estudiante, omitiendo...")
        return None
    
    # Verificar si el estudiante existe
    if estudiante_id not in estudiantes_ids:
        # Verificar si existe en la base de datos
        if not Estudiante.objects.filter(id=estudiante_id).exists():
            print(f"⚠️ Estudiante {estudiante_id} no existe para agenda {pk}, omitiendo...")
            return None
        else:
            # Si existe en la BD pero no en estudiantes_ids, agregarlo
            estudiantes_ids.add(estudiante_id)
    
    # Crear o actualizar agenda
    try:
        obj, created = AgendaEstudiante.objects.update_or_create(
            id=pk,
            defaults=fields
        )
        
        if created:
            estadisticas['registros_creados'] += 1
            print(f"  ✓ Agenda {pk} creada para estudiante {estudiante_id}")
        else:
            estadisticas['registros_actualizados'] += 1
            print(f"  ✓ Agenda {pk} actualizada para estudiante {estudiante_id}")
        
        return obj
    except Exception as e:
        print(f"❌ Error en agenda {pk}: {str(e)}")
        return None

def restaurar_sesion_individual(obj_data, estadisticas, agendas_ids):
    """Restaura una sesión individual - VERSIÓN CORREGIDA"""
    from agenda.models import Sesion, AgendaEstudiante
    
    pk = obj_data.get('pk')
    fields = obj_data.get('fields', {})
    
    fields = convertir_campos_desde_json(fields)
    
    # Verificar que la agenda existe
    agenda_id = fields.get('agenda')
    
    if not agenda_id:
        print(f"⚠️ Sesión {pk} no tiene agenda, omitiendo...")
        return None
    
    # Verificar si la agenda existe
    if agenda_id not in agendas_ids:
        # Verificar si existe en la base de datos
        if not AgendaEstudiante.objects.filter(id=agenda_id).exists():
            print(f"⚠️ Agenda {agenda_id} no existe para sesión {pk}, omitiendo...")
            return None
        else:
            # Si existe en la BD pero no en agendas_ids, agregarla
            agendas_ids.add(agenda_id)
    
    # Crear o actualizar sesión
    try:
        obj, created = Sesion.objects.update_or_create(
            id=pk,
            defaults=fields
        )
        
        if created:
            estadisticas['registros_creados'] += 1
            print(f"  ✓ Sesión {pk} creada para agenda {agenda_id}")
        else:
            estadisticas['registros_actualizados'] += 1
            print(f"  ✓ Sesión {pk} actualizada para agenda {agenda_id}")
        
        return obj
    except Exception as e:
        print(f"❌ Error en sesión {pk}: {str(e)}")
        return None

def convertir_campos_desde_json(fields):
    """Convierte campos desde JSON a tipos Python"""
    for key, value in fields.items():
        if isinstance(value, str):
            try:
                # Intentar convertir fechas/horas
                if 'T' in value:  # DateTime ISO
                    if value.endswith('Z'):
                        fields[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    else:
                        fields[key] = datetime.fromisoformat(value)
                elif len(value) == 10 and value.count('-') == 2:  # Date ISO
                    fields[key] = date.fromisoformat(value)
                elif len(value) >= 5 and ':' in value:  # Time ISO
                    try:
                        fields[key] = time.fromisoformat(value)
                    except ValueError:
                        try:
                            dt = datetime.fromisoformat(value)
                            fields[key] = dt.time()
                        except:
                            pass
            except Exception as e:
                # Si no se puede convertir, dejar como está
                pass
    return fields

def mostrar_resultados_restauracion(request, estadisticas, nombre_archivo, estudiantes_ids=None, agendas_ids=None):
    """Muestra resultados de la restauración"""
    
    # Mostrar mensaje de éxito
    if estadisticas['registros_creados'] > 0:
        mensaje = f"✅ Restauración completada: {estadisticas['registros_creados']} registros creados"
        if estadisticas['registros_actualizados'] > 0:
            mensaje += f", {estadisticas['registros_actualizados']} actualizados"
        messages.success(request, mensaje)
    elif estadisticas['registros_actualizados'] > 0:
        messages.success(request, f"✅ Restauración completada: {estadisticas['registros_actualizados']} registros actualizados")
    else:
        messages.warning(request, "⚠️ No se crearon ni actualizaron registros")
    
    # Mostrar estadísticas
    if estudiantes_ids:
        messages.info(request, f"👥 Estudiantes procesados: {len(estudiantes_ids)}")
    
    if agendas_ids:
        messages.info(request, f"📅 Agendas procesadas: {len(agendas_ids)}")
    
    # Mostrar errores si los hay
    if estadisticas['errores']:
        # Mostrar primeros 3 errores detallados
        for error in estadisticas['errores'][:3]:
            messages.warning(request, f"⚠️ {error}")
        
        if len(estadisticas['errores']) > 3:
            messages.warning(request, f"⚠️ ... y {len(estadisticas['errores']) - 3} errores más")
    
    return redirect('backups:dashboard')

@login_required
@require_POST
def eliminar_backup(request, backup_id):
    """Elimina un backup"""
    backup = get_object_or_404(Backup, id=backup_id)
    
    try:
        # Eliminar archivo físico
        if backup.archivo:
            backup.archivo.delete(save=False)
        
        # Eliminar registro
        nombre_backup = backup.nombre
        backup.delete()
        
        messages.success(request, f'✅ Backup "{nombre_backup}" eliminado correctamente')
        
    except Exception as e:
        messages.error(request, f'❌ Error al eliminar: {str(e)}')
    
    return redirect('backups:dashboard')

@login_required
@require_GET
def info_backup(request, backup_id):
    """Información detallada de un backup"""
    try:
        backup = Backup.objects.get(id=backup_id)
        
        info = {
            'id': backup.id,
            'nombre': backup.nombre,
            'descripcion': backup.descripcion,
            'fecha': backup.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'usuario': backup.usuario.username if backup.usuario else 'Sistema',
            'tamano': backup.tamano_formateado,
            'estado': backup.estado,
            'tiene_archivo': bool(backup.archivo),
            'estadisticas': {}
        }
        
        # Contar registros por modelo si hay datos JSON
        if backup.datos_json and 'datos' in backup.datos_json:
            for app_label, modelos in backup.datos_json['datos'].items():
                info['estadisticas'][app_label] = {}
                for model_name, info_modelo in modelos.items():
                    if 'count' in info_modelo:
                        info['estadisticas'][app_label][model_name] = info_modelo['count']
        
        return JsonResponse(info)
        
    except Backup.DoesNotExist:
        return JsonResponse({'error': 'Backup no encontrado'}, status=404)