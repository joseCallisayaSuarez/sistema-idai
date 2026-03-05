# estadisticas/urls.py
from django.urls import path
from . import views

app_name = 'estadisticas'

urlpatterns = [
    path('', views.dashboard_estadisticas, name='dashboard_estadisticas'),
    path('actualizar/', views.actualizar_estadisticas, name='actualizar_estadisticas'),
    path('pdf/', views.generar_pdf_estadisticas, name='generar_pdf_estadisticas'),
  
]