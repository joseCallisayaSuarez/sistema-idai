from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



class MiLoginForm(AuthenticationForm):
    username = forms.CharField(label=_("Usuario"))
    password = forms.CharField(label=_("Contraseña"), widget=forms.PasswordInput)

    # 🔹 Mensajes de error completamente personalizados
    error_messages = {
        'invalid_login': _("Por favor, introduzca un nombre de usuario y clave correctos."),
        'inactive': _("Esta cuenta está desactivada."),
    }
