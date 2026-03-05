from django.db import models
from django.conf import settings

class Backup(models.Model):
    """Modelo para almacenar información de backups"""
    
    # Campos básicos
    nombre = models.CharField(
        max_length=255,
        verbose_name="Nombre del Backup",
        help_text="Ej: Backup completo diciembre 2024"
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Detalles sobre lo que contiene este backup"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    # ✅ IMPORTANTE: Así se referencia al modelo Usuario personalizado
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Esto se resuelve como 'usuarios.Usuario'
        on_delete=models.SET_NULL,  # Si se elimina el usuario, el backup queda
        null=True,
        blank=True,
        verbose_name="Usuario que creó el backup"
    )
    
    # Archivo de backup
    archivo = models.FileField(
        upload_to='backups/%Y/%m/%d/',  # Organiza por fecha
        blank=True,
        null=True,
        verbose_name="Archivo de backup"
    )
    
    # Tamaño en bytes
    tamano = models.BigIntegerField(
        default=0,
        verbose_name="Tamaño del archivo (bytes)"
    )
    
    # Estados posibles
    ESTADO_CHOICES = [
        ('completado', '✅ Completado'),
        ('fallido', '❌ Fallido'),
        ('en_progreso', '⏳ En progreso'),
    ]
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='en_progreso',
        verbose_name="Estado del backup"
    )
    
    # Datos del backup en formato JSON
    datos_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos del backup (JSON)"
    )
    
    class Meta:
        verbose_name = "Copia de Seguridad"
        verbose_name_plural = "Copias de Seguridad"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['fecha_creacion']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha_creacion.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def tamano_formateado(self):
        """Devuelve el tamaño en formato legible"""
        if self.tamano == 0:
            return "0 B"
        
        unidades = ['B', 'KB', 'MB', 'GB', 'TB']
        tamano = float(self.tamano)
        
        for unidad in unidades:
            if tamano < 1024.0:
                return f"{tamano:.2f} {unidad}"
            tamano /= 1024.0
        
        return f"{tamano:.2f} {unidades[-1]}"
    
    @property
    def es_descargable(self):
        """Verifica si el backup tiene archivo y está completado"""
        return bool(self.archivo) and self.estado == 'completado'