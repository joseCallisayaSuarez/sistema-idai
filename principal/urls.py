# principal/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ✅ PRIMERO incluye la app usuarios (que tiene password_reset)
    path('', include('usuarios.urls')),
    
    # ✅ LUEGO el login personalizado
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Tus otras apps
    path('estudiantes/', include('estudiantes.urls')),
    path('agenda/', include('agenda.urls')),
    path('estadisticas/', include('estadisticas.urls')),
    path('registro_evolucion/', include('registro_evolucion.urls')),
    path('backups/', include('backups.urls')),
    
    # Redirección
    path('', lambda request: redirect('/login/')),
]