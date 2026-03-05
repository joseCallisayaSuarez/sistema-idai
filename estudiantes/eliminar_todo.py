# estudiantes/eliminar_todo.py

from estudiantes.models import Estudiante, Tutor

def eliminar_todo():
    # Contar y eliminar todos los estudiantes
    total_estudiantes = Estudiante.objects.count()
    Estudiante.objects.all().delete()
    print(f"✅ Se eliminaron {total_estudiantes} estudiantes.")

    # Contar y eliminar todos los tutores
    total_tutores = Tutor.objects.count()
    Tutor.objects.all().delete()
    print(f"✅ Se eliminaron {total_tutores} tutores.")
