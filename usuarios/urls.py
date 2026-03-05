from django.urls import path
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.login_usuario, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard_admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard_usuario/', views.dashboard_usuario, name='dashboard_usuario'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset_form.html'
    ), name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),
    path("logout/", views.logout_usuario, name="logout"),

    
    path('usuario/eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),

]
    

