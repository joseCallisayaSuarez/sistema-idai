from django.db import models

# -------------------------
# Constantes / choices
# -------------------------
GENERO_CHOICES = [
    ('M', 'Masculino'),
    ('F', 'Femenino'),
]

NIVEL_CHOICES = [
    ('IFC', 'IFC'),
    ('PCV', 'PCV'),
    ('SCP', 'SCP'),
]

GRADO_CHOICES = [
    ('1ro', '1ro'),
    ('2do', '2do'),
    ('3ro', '3ro'),
    ('4to', '4to'),
    ('5to', '5to'),
    ('6to', '6to'),
]

EVALUACION_CHOICES = [
    ('lectoescritura', 'Lectoescritura'),
    ('razonamiento_logico', 'Razonamiento Lógico Matemático'),
    ('atencion_memoria', 'Atención y Memoria'),
    ('psicoeducativa', 'Evaluación Psicoeducativa'),
    ('psicopedagogica', 'Evaluación Psicopedagógica'),
    ('multidisciplinaria', 'Evaluación Multidisciplinaria'),
]

PROGRAMA_CHOICES = [
    ('lectoescritura', 'Lectoescritura'),
    ('razonamiento_logico', 'Razonamiento Lógico Matemático'),
    ('signos_riesgo', 'Signos de Riesgo'),
    ('atencion_disperza', 'Atención Dispersa'),
    ('discapacidad_leve', 'Discapacidad Intelectual Leve'),
    ('otro', 'Otro'),
]

MODALIDAD_CHOICES = [
    ('directa', 'Atención Directa'),
    ('indirecta', 'Atención Indirecta'),
]

SEMESTRE_CHOICES = [
    ('1', 'Primer Semestre'),
    ('2', 'Segundo Semestre'),
]
GESTION_CHOICES = [
    ('2019', '2019'),
    ('2020', '2020'),
    ('2021', '2021'),
    ('2022', '2022'),
    ('2023', '2023'),
    ('2024', '2024'),
    ('2025', '2025'),
    ('2026', '2026'),
    ('2027', '2027'),
    ('2028', '2028'),
    ('2029', '2029'),
    ('2030', '2030'),
    ('2031', '2031'),
    ('2032', '2032'),
    ('2033', '2033'),
    ('2034', '2034'),
]


# -------------------------
# Tutor / Padre
# -------------------------
class Tutor(models.Model):
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    nombres = models.CharField(max_length=150)
    ci = models.CharField(max_length=20, unique=True)
    parentesco = models.CharField(max_length=50, blank=True, null=True)
    ocupacion = models.CharField(max_length=100, blank=True, null=True)

    zona = models.CharField(max_length=120, blank=True, null=True)
    avenida = models.CharField(max_length=120, blank=True, null=True)
    nro_vivienda = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True, unique=True)
    celular = models.CharField(max_length=15, blank=True, null=True, unique=True)
    

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno}"


# -------------------------
# Estudiante
# -------------------------
class Estudiante(models.Model):
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    nombres = models.CharField(max_length=150)
    pais = models.CharField(max_length=80)
    departamento = models.CharField(max_length=80)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    edad = models.PositiveSmallIntegerField()
    documento_identidad = models.CharField(max_length=20, unique=True)
    codigo_rude = models.CharField(max_length=30, unique=True)
    colegio_procedencia = models.CharField(max_length=150, blank=True, null=True)
    nivel = models.CharField(max_length=3, choices=NIVEL_CHOICES)
    grado = models.CharField(max_length=4, choices=GRADO_CHOICES)
    semestre = models.CharField(max_length=1, choices=SEMESTRE_CHOICES, default='1')  # ← NUEVO CAMP
    maestra_aula = models.CharField(max_length=100, blank=True, null=True)  # ← NUEVO CAMPO
    gestion_ingreso = models.CharField(max_length=4, choices=GESTION_CHOICES, default='2024')

    zona = models.CharField(max_length=120)
    avenida = models.CharField(max_length=120, blank=True, null=True)
    nro_vivienda = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True, unique=True)
    celular = models.CharField(max_length=15, blank=True, null=True, unique=True)

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='estudiantes')

    resultados_evaluacion = models.JSONField(default=list, blank=True)
    evaluacion_requerida = models.CharField(max_length=200, blank=True, null=True)
    programa_apoyo = models.JSONField(default=list, blank=True)
    programa_otro = models.CharField(max_length=200, blank=True, null=True)

    modalidad_atencion = models.CharField(max_length=20, choices=MODALIDAD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno}"
