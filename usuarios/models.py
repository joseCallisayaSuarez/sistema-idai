from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('usuario', 'Usuario Común'),
    )
    rol = models.CharField(max_length=10, choices=ROLES, default='usuario')

    def __str__(self):
        return f"{self.username} ({self.rol})"
