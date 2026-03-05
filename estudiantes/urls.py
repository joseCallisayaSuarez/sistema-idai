from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar_estudiante, name='registrar_estudiante'),
    path('', views.lista_estudiantes, name='lista_estudiantes'),
    path('editar/<int:pk>/', views.editar_estudiante, name='editar_estudiante'),
    path('eliminar/<int:pk>/', views.eliminar_estudiante, name='eliminar_estudiante'),
    path('estudiantes/ver/<int:pk>/', views.ver_estudiante, name='ver_estudiante'),
    #NUEVO
    path('pdf/lista/', views.generar_pdf_estudiantes, name='generar_pdf_estudiantes'),
    
]
