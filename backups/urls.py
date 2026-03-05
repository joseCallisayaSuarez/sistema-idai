from django.urls import path
from . import views

app_name = 'backups'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('crear/', views.crear_backup, name='crear_backup'),
    path('descargar/<int:backup_id>/', views.descargar_backup, name='descargar_backup'),
  
    path('restaurar/', views.restaurar_backup, name='restaurar_backup'),
    path('eliminar/<int:backup_id>/', views.eliminar_backup, name='eliminar_backup'),
    path('info/<int:backup_id>/', views.info_backup, name='info_backup'),
     path('restaurar/', views.restaurar_backup, name='restaurar_backup'),  # 👈 NUEVA
]