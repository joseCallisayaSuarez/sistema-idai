import os
import json
from datetime import datetime, time, date, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core import serializers
from django.apps import apps
from django.db import transaction
from django.db.models import Model
from decimal import Decimal
from backups.models import Backup

class CustomJSONEncoder(json.JSONEncoder):
    """Encoder personalizado para manejar tipos especiales de Django"""
    
    def default(self, obj):
        # Manejar objetos time
        if isinstance(obj, time):
            return obj.isoformat()
        
        # Manejar objetos date
        elif isinstance(obj, date):
            return obj.isoformat()
        
        # Manejar objetos datetime
        elif isinstance(obj, datetime):
            return obj.isoformat()
        
        # Manejar objetos Decimal
        elif isinstance(obj, Decimal):
            return float(obj)
        
        # Manejar objetos timedelta
        elif isinstance(obj, timedelta):
            return str(obj)
        
        # Manejar objetos UUID
        elif hasattr(obj, 'hex'):
            return str(obj)
        
        # Para modelos Django, usar su representación string
        elif isinstance(obj, Model):
            return str(obj)
        
        # Para cualquier otro tipo, usar el método por defecto
        return super().default(obj)


class Command(BaseCommand):
    help = 'Crea un backup completo del sistema'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario_id',
            type=int,
            help='ID del usuario que solicita el backup'
        )
        parser.add_argument(
            '--nombre',
            type=str,
            default='',
            help='Nombre personalizado para el backup'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Modo debug para ver detalles'
        )

    def handle(self, *args, **options):
        usuario_id = options.get('usuario_id')
        nombre_personalizado = options.get('nombre', '')
        debug = options.get('debug', False)
        
        self.stdout.write("=" * 50)
        self.stdout.write("🚀 INICIANDO PROCESO DE BACKUP")
        self.stdout.write("=" * 50)
        
        try:
            # Obtener el modelo Usuario personalizado
            Usuario = apps.get_model(settings.AUTH_USER_MODEL)
            
            if usuario_id:
                usuario = Usuario.objects.get(id=usuario_id)
            else:
                usuario = Usuario.objects.first()
                
            self.stdout.write(f"👤 Usuario: {usuario.username if usuario else 'No encontrado'}")
            
        except Exception as e:
            if debug:
                self.stdout.write(self.style.WARNING(f"⚠️ Error obteniendo usuario: {str(e)}"))
            usuario = None
        
        # Crear registro de backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre = nombre_personalizado if nombre_personalizado else f"Backup {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        backup = Backup.objects.create(
            nombre=nombre,
            descripcion=f"Backup automático del sistema",
            usuario=usuario,
            estado='en_progreso'
        )
        
        self.stdout.write(f"📝 Backup creado en BD: {backup.id}")
        
        try:
            with transaction.atomic():
                # 1. Recolectar datos
                self.stdout.write("📊 Recolectando datos del sistema...")
                datos_completos = self.recolectar_datos_completos(debug)
                
                # 2. Crear directorio si no existe
                backup_dir = os.path.join(settings.MEDIA_ROOT, 'backups')
                os.makedirs(backup_dir, exist_ok=True)
                
                # 3. Crear archivo JSON
                nombre_json = f"backup_{timestamp}_{backup.id}.json"
                ruta_json = os.path.join(backup_dir, nombre_json)
                
                self.stdout.write(f"💾 Guardando archivo: {ruta_json}")
                
                # Usar nuestro encoder personalizado
                with open(ruta_json, 'w', encoding='utf-8') as f:
                    json.dump(datos_completos, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)
                
                # 4. Actualizar backup
                backup.datos_json = datos_completos
                backup.archivo.name = f'backups/{nombre_json}'
                backup.tamano = os.path.getsize(ruta_json)
                backup.estado = 'completado'
                backup.save()
                
                self.stdout.write("=" * 50)
                self.stdout.write(self.style.SUCCESS("✅ BACKUP COMPLETADO EXITOSAMENTE"))
                self.stdout.write(f"📁 Archivo: {ruta_json}")
                self.stdout.write(f"📏 Tamaño: {backup.tamano_formateado}")
                self.stdout.write("=" * 50)
                
        except Exception as e:
            self.stdout.write("=" * 50)
            self.stdout.write(self.style.ERROR("❌ ERROR EN BACKUP"))
            self.stdout.write(f"Error: {str(e)}")
            self.stdout.write("=" * 50)
            
            # Actualizar estado a fallido
            backup.estado = 'fallido'
            backup.descripcion = f"Error: {str(e)[:200]}"
            backup.save()
            
            if debug:
                import traceback
                traceback.print_exc()

    def recolectar_datos_completos(self, debug=False):
        """Recolecta datos de TODOS los módulos del sistema"""
        datos = {
            'metadata': {
                'fecha_creacion': datetime.now().isoformat(),
                'sistema': 'Sistema DIF - Agenda',
                'version': '1.0'
            },
            'datos': {}
        }
        
        # Lista de APPS A BACKUPEAR
        apps_a_backupear = [
            'agenda',
            'usuarios',
            'estudiantes',
            'estadisticas',
            'registro_evolucion',

        ]
        
        for app_label in apps_a_backupear:
            try:
                app_config = apps.get_app_config(app_label)
                datos_app = {}
                total_registros = 0
                
                self.stdout.write(f"\n📦 Procesando app: {app_label}")
                
                for model in app_config.get_models():
                    try:
                        # Contar registros
                        count = model.objects.count()
                        total_registros += count
                        
                        if debug:
                            self.stdout.write(f"   • {model._meta.model_name}: {count} registros")
                        
                        # Solo serializar si hay datos
                        if count > 0:
                            # Serializar con nuestro método personalizado
                            objetos = self.serializar_modelo(model)
                            
                            datos_app[model._meta.model_name] = {
                                'count': count,
                                'objetos': objetos
                            }
                        else:
                            datos_app[model._meta.model_name] = {
                                'count': 0,
                                'objetos': []
                            }
                            
                    except Exception as e:
                        if debug:
                            self.stdout.write(self.style.WARNING(f"   ✗ Error en {model._meta.model_name}: {str(e)}"))
                        datos_app[model._meta.model_name] = {
                            'error': str(e),
                            'count': 0
                        }
                
                datos['datos'][app_label] = datos_app
                self.stdout.write(self.style.SUCCESS(f"   ✓ {app_label}: {total_registros} registros totales"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Error en app {app_label}: {str(e)}"))
                datos['datos'][app_label] = {
                    'error': f'No se pudo acceder a la app: {str(e)}'
                }
        
        # Mostrar resumen
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("📊 RESUMEN DEL BACKUP")
        self.stdout.write("=" * 50)
        
        total_modelos = 0
        total_objetos = 0
        
        for app_label, app_data in datos['datos'].items():
            modelos_app = len(app_data)
            objetos_app = sum(modelo.get('count', 0) for modelo in app_data.values())
            
            self.stdout.write(f"{app_label}: {modelos_app} modelos, {objetos_app} registros")
            total_modelos += modelos_app
            total_objetos += objetos_app
        
        self.stdout.write("-" * 30)
        self.stdout.write(f"TOTAL: {total_modelos} modelos, {total_objetos} registros")
        
        return datos

    def serializar_modelo(self, model):
        """Serializa un modelo manejando tipos especiales"""
        objetos = model.objects.all()
        datos_serializados = []
        
        for obj in objetos:
            try:
                # Convertir objeto a diccionario
                obj_dict = {
                    'pk': obj.pk,
                    'model': f"{model._meta.app_label}.{model._meta.model_name}",
                    'fields': {}
                }
                
                # Obtener todos los campos
                for field in model._meta.fields:
                    field_name = field.name
                    field_value = getattr(obj, field_name)
                    
                    # Convertir tipos especiales
                    if field_value is None:
                        obj_dict['fields'][field_name] = None
                    
                    # Manejar objetos time
                    elif isinstance(field_value, time):
                        obj_dict['fields'][field_name] = field_value.isoformat()
                    
                    # Manejar objetos date
                    elif isinstance(field_value, date):
                        obj_dict['fields'][field_name] = field_value.isoformat()
                    
                    # Manejar objetos datetime
                    elif isinstance(field_value, datetime):
                        obj_dict['fields'][field_name] = field_value.isoformat()
                    
                    # Manejar objetos Decimal
                    elif isinstance(field_value, Decimal):
                        obj_dict['fields'][field_name] = float(field_value)
                    
                    # Manejar ForeignKey (solo guardar el ID)
                    elif hasattr(field, 'remote_field') and field.remote_field:
                        if field_value:
                            obj_dict['fields'][field_name] = field_value.pk
                        else:
                            obj_dict['fields'][field_name] = None
                    
                    # Para cualquier otro tipo, usar str() si no es serializable
                    else:
                        try:
                            # Intentar serializar normalmente
                            json.dumps(field_value)
                            obj_dict['fields'][field_name] = field_value
                        except (TypeError, ValueError):
                            # Si falla, usar representación string
                            obj_dict['fields'][field_name] = str(field_value)
                
                datos_serializados.append(obj_dict)
                
            except Exception as e:
                # Si hay error con un objeto, continuar con los demás
                datos_serializados.append({
                    'error': f"Error serializando objeto {obj.pk}: {str(e)}",
                    'pk': obj.pk if hasattr(obj, 'pk') else None
                })
                continue
        
        return datos_serializados