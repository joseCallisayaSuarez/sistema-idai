from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm, MiLoginForm
from .models import Usuario  
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404

# 🧾 Registro de usuario (solo crea usuarios comunes)
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Validaciones básicas
        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'register.html')

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'register.html')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return render(request, 'register.html')

        # Crear usuario normal (no admin)
        user = Usuario(
            username=username,
            email=email,
            password=make_password(password1),
            rol='usuario'  # Por defecto usuario común
        )
        user.save()

        messages.success(request, 'Registro exitoso. Inicia sesión para continuar.')
        return redirect('login')

    return render(request, 'register.html')


# 🔐 Login con redirección según el rol
def login_usuario(request):
    form = MiLoginForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.rol == "admin":
                return redirect('dashboard_admin')
            else:
                return redirect('dashboard_usuario')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    return render(request, "login.html", {"form": form})


# 🚪 Logout
def logout_usuario(request):
    logout(request)
    return redirect('login')


# 🧭 Dashboard de administrador (solo admin)
@login_required(login_url='login')
def dashboard_admin(request):
    if request.user.rol != 'admin':
        return redirect('dashboard_admin')
    usuarios = Usuario.objects.filter(rol='usuario')
    return render(request, "dashboard_admin.html", {"usuarios": usuarios})


# 👤 Dashboard de usuario común
@login_required(login_url='login')
def dashboard_usuario(request):
    return render(request, "dashboard_usuario.html")


# 🔁 Redirección principal al login
def home(request):
    return redirect('login')

def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('dashboard_admin')
    return render(request, 'usuario_confirmar_eliminar.html', {'usuario': usuario})