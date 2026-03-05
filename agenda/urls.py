from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    # Flujo principal
    path('', views.buscar_estudiante_agenda, name='buscar_estudiante'),
    path('crear-agenda/<int:estudiante_id>/', views.crear_agenda, name='crear_agenda'),
    path('calendario/', views.calendario_general, name='calendario_general'),
    path('registrar-asistencia/<int:sesion_id>/', views.registrar_asistencia, name='registrar_asistencia'),
    
    # Vistas adicionales
    path('agendas/', views.lista_agendas, name='lista_agendas'),
    path('agenda/<int:agenda_id>/', views.detalle_agenda, name='detalle_agenda'),
    path('agenda/<int:agenda_id>/editar/', views.editar_agenda, name='editar_agenda'),
    path('agenda/<int:agenda_id>/desactivar/', views.desactivar_agenda, name='desactivar_agenda'),
    path('agenda/<int:agenda_id>/activar/', views.activar_agenda, name='activar_agenda'),
    path('agenda/<int:agenda_id>/eliminar/', views.eliminar_agenda, name='eliminar_agenda'),

    path('agenda/<int:agenda_id>/pdf/', views.generar_pdf_agenda, name='generar_pdf_agenda'),
    


    
]