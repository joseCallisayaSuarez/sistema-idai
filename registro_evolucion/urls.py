# registro_evolucion/urls.py
from django.urls import path
from . import views

app_name = 'registro_evolucion'

urlpatterns = [
    # Informes Finales
    path('informes/', views.lista_informes_finales, name='lista_informes'),
    path('informes/nuevo/', views.crear_informe_final, name='crear_informe'),
    path('informes/<int:pk>/editar/', views.editar_informe_final, name='editar_informe'),
    path('informes/<int:pk>/', views.ver_informe_final, name='ver_informe'),
    path('informes/<int:pk>/pdf/', views.generar_pdf_informe, name='generar_pdf'),
    path('informes/<int:pk>/eliminar/', views.eliminar_informe_final, name='eliminar_informe'),
    
    # AJAX
    path('ajax/buscar-estudiante/', views.buscar_estudiante_ajax, name='buscar_estudiante_ajax'),
    path('ajax/areas-desarrollo/', views.cargar_areas_desarrollo, name='cargar_areas_ajax'),
    path('informes/nuevo/estudiante/<int:estudiante_id>/', views.crear_informe_desde_estudiante, name='crear_informe_estudiante'),
]