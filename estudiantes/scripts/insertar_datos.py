from faker import Faker
import random
from datetime import date
from estudiantes.models import Estudiante, PadreTutor, ModuloEstudiante

def run():
    fake = Faker('es_ES')
    niveles = ['Inicial', 'Primaria', 'Secundaria']

    for i in range(1, 51):
        # === Crear Estudiante ===
        fecha_nac = fake.date_of_birth(minimum_age=6, maximum_age=15)
        edad = date.today().year - fecha_nac.year

        estudiante = Estudiante.objects.create(
            ci=str(7000000 + i),
            nombre=fake.first_name(),
            apellido_paterno=fake.last_name(),
            apellido_materno=fake.last_name(),
            fecha_nacimiento=fecha_nac,
            edad=edad,
            genero=random.choice(['M', 'F']),
            nro_rude=f"RUDE{i:03d}",
            colegio_procedencia=fake.company(),
            nivel=random.choice(niveles),
            direccion=fake.street_address()
        )

        # === Crear Padre/Tutor asociado ===
        fecha_nac_tutor = fake.date_of_birth(minimum_age=30, maximum_age=55)
        edad_tutor = date.today().year - fecha_nac_tutor.year

        PadreTutor.objects.create(
            estudiante=estudiante,
            ci=str(8000000 + i),
            nombre=fake.first_name(),
            apellido_paterno=fake.last_name(),
            apellido_materno=fake.last_name(),
            fecha_nacimiento=fecha_nac_tutor,
            edad=edad_tutor,
            genero=random.choice(['M', 'F']),
            direccion=fake.street_address()
        )

        # === Crear Módulo asociado ===
        ModuloEstudiante.objects.create(
            estudiante=estudiante,
            lectura=random.choice([True, False]),
            matematica=random.choice([True, False])
        )

    print("✅ Se insertaron correctamente 50 estudiantes con sus tutores y módulos.")
