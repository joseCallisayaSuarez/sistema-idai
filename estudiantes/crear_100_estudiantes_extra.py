# estudiantes/crear_100_estudiantes_extra.py

from estudiantes.models import Estudiante, Tutor
from datetime import date
import random

def crear_100_estudiantes_extra():
    # Zonas reales de La Paz, Bolivia
    zonas_la_paz = [
        "Centro - Sopocachi", "Zona Sur - Calacoto", "Zona Sur - Achumani", 
        "Zona Sur - Obrajes", "Zona Norte - Villa Fátima", "Zona Norte - Miraflores",
        "Zona Este - San Pedro", "Zona Oeste - Alto Obrajes", "Zona Sur - Cota Cota",
        "Zona Norte - Cotahuma", "Zona Centro - San Jorge", "Zona Sur - Irpavi",
        "Zona Sur - Següencoma", "Zona Norte - Sopocachi Bajo", "Zona Este - Munaypata",
        "Zona Oeste - Tembladerani", "Zona Sur - Bolognia", "Zona Norte - Llojeta",
        "Zona Este - Pura Pura", "Zona Oeste - Alto San Pedro",
        "Zona Sur - San Miguel", "Zona Norte - San Antonio", "Zona Este - Alto Lima",
        "Zona Oeste - Chasquipampa", "Zona Sur - Las Lomas", "Zona Norte - Ciudad Satélite",
        "Zona Este - Villa Armonía", "Zona Oeste - Pampahasi", "Zona Sur - Alto Auquisamaña",
        "Zona Norte - Callapa", "Zona Este - Kupini", "Zona Oeste - Munaypata",
        "Zona Sur - Alto Següencoma", "Zona Norte - Alto Miraflores", "Zona Este - San Martín",
        "Zona Oeste - Alto San Antonio", "Zona Sur - Valle de las Flores", "Zona Norte - Villa Dolores",
        "Zona Este - Alto Villa Victoria", "Zona Oeste - Alto Chijini"
    ]
    
    avenidas_la_paz = [
        "Av. 16 de Julio", "Av. Arce", "Av. 6 de Agosto", "Av. Camacho", 
        "Av. Mariscal Santa Cruz", "Av. Villazón", "Av. Busch", "Av. Perú",
        "Av. Montes", "Av. Buenos Aires", "Av. Hernando Siles", "Av. del Poeta",
        "Av. Costanera", "Av. del Ejército", "Av. Kollasuyo", "Av. República",
        "Av. Simón Bolívar", "Av. Saavedra", "Av. Landaeta", "Av. Ballivián",
        "Av. América", "Av. del Policía", "Av. Gualberto Villarroel", "Av. La Paz",
        "Av. Circunvalación", "Av. Alexander", "Av. Juan Pablo II", "Av. Perú",
        "Av. Bolivia", "Av. Sucre", "Av. Potosí", "Av. Oruro", "Av. Tarija",
        "Av. Santa Cruz", "Av. Beni", "Av. Pando", "Av. Chuquisaca", "Av. Cochabamba",
        "Av. Illimani", "Av. Murillo"
    ]
    
    # Nombres reales de maestras bolivianas
    maestras_aula = [
        "María Elena Vargas", "Ana Luisa Fernández", "Carmen Rosa Torrez", 
        "Patricia Mendez López", "Susana Ríos Quiroga", "Elena Castro Morales",
        "Gabriela Paredes Suárez", "Claudia Rojas Arce", "Verónica Salazar Paz",
        "Jimena Valdez Ribera", "Rosa María Blanco", "Lucía Andrade Camacho",
        "Silvia Peña Ortiz", "Daniela Montesinos", "Carolina Serrano Guzmán",
        "Paola Núñez Castillo", "Andrea Zambrana Rojas", "Natalia Mercado Flores",
        "Valeria Durán Herrera", "Liliana Cordero Miranda", "Sofia Mendoza Paredes",
        "Isabel Rojas Gutierrez", "Carmen Julia Velasco", "Martha Patricia Andrade",
        "Rocio Alejandra Soto", "Gladys Mabel Cabrera", "Diana Carolina Ríos",
        "Ximena Patricia Núñez", "Lorena Elizabeth Torrico", "Sandra Marcela Arce"
    ]

    # Colegios de La Paz
    colegios_la_paz = [
        "REPUBLICA DE CANADA", "SANTA ROSA GRANDE", "BOLIVIA", "SANTA CRUZ",
        "COCHABAMBA", "SUCRE", "ORURO", "TARIJA", "BENI", "POTOSI", "LA PAZ",
        "AYACUCHO", "AMERICA", "SAN CALIXTO", "LA SALLE", "SAN ANDRES",
        "MARIANO BAPTISTA", "JUAN XXIII", "SAN IGNACIO", "MEXICO",
        "DON BOSCO", "SANTO TOMAS", "SAN VICENTE", "SAGRADO CORAZON",
        "SAN JOSE", "SAN FRANCISCO", "SAN PEDRO", "SAN MARCOS", "SAN LUCAS",
        "SAN MATEO", "SANTA ANA", "SANTA MARIA", "SANTA ISABEL", "SANTA TERESA",
        "SANTA ROSA", "SANTA LUCIA", "SANTA BARBARA", "SANTA MONICA", "SANTA CLARA"
    ]

    # Apellidos comunes para estudiantes
    apellidos_estudiantes = [
        "Mamani", "Quispe", "Huanca", "Choque", "Fernandez", "Garcia", "Lopez", 
        "Rodriguez", "Perez", "Gonzales", "Martinez", "Sanchez", "Ramirez", 
        "Flores", "Vargas", "Rojas", "Castro", "Romero", "Suarez", "Alvarez",
        "Torrez", "Rivera", "Medina", "Aguilar", "Paredes", "Cruz", "Reyes",
        "Mendoza", "Salazar", "Herrera", "Castillo", "Guiterrez", "Chavez",
        "Velasco", "Escobar", "Pinto", "Miranda", "Camacho", "Cabrera", "Rios"
    ]

    # Nombres para estudiantes
    nombres_masculinos = [
        "Juan", "Carlos", "Luis", "Miguel", "José", "Antonio", "Jorge", 
        "Roberto", "David", "Francisco", "Mario", "Pedro", "Fernando", 
        "Ricardo", "Eduardo", "Alberto", "Ramiro", "Sergio", "Andrés", "Diego",
        "Javier", "Daniel", "Pablo", "Raul", "Oscar", "Victor", "Hugo",
        "Mauricio", "Walter", "Samuel", "Leonardo", "Rodrigo", "Sebastian",
        "Matias", "Gabriel", "Cristian", "Alex", "Marco", "Fabian", "Ivan"
    ]

    nombres_femeninos = [
        "María", "Ana", "Rosa", "Carmen", "Laura", "Patricia", "Elena", 
        "Isabel", "Lucía", "Silvia", "Gabriela", "Verónica", "Claudia", 
        "Natalia", "Andrea", "Carolina", "Daniela", "Valeria", "Jimena", "Paola",
        "Sofia", "Camila", "Valentina", "Fernanda", "Alejandra", "Monica",
        "Diana", "Ximena", "Lorena", "Sandra", "Rocio", "Gladys", "Martha",
        "Julia", "Beatriz", "Adriana", "Gloria", "Ruth", "Esther", "Miriam"
    ]

    def generar_telefono(i):
        return f"2{str(8000000 + i).zfill(7)}"  # Números únicos

    def generar_celular(i):
        prefix = random.choice([6, 7])
        return f"{prefix}{str(8000000 + i).zfill(7)}"  # Números únicos

    # Apellidos comunes para tutores
    apellidos_tutores = [
        "Gonzales", "Rodríguez", "Fernández", "López", "Martínez", 
        "García", "Pérez", "Gómez", "Hernández", "Díaz", "Torres", 
        "Ramírez", "Flores", "Vargas", "Rojas", "Castro", "Romero", 
        "Suárez", "Alvarez", "Ruiz", "Mendoza", "Salazar", "Herrera",
        "Castillo", "Guiterrez", "Chavez", "Velasco", "Escobar", "Pinto",
        "Miranda", "Camacho", "Cabrera", "Rios", "Medina", "Aguilar",
        "Paredes", "Cruz", "Reyes", "Sanchez", "Morales"
    ]
    
    nombres_tutores_hombres = [
        "Juan", "Carlos", "Luis", "Miguel", "José", "Antonio", "Jorge", 
        "Roberto", "David", "Francisco", "Mario", "Pedro", "Fernando", 
        "Ricardo", "Eduardo", "Alberto", "Ramiro", "Sergio", "Andrés", "Diego",
        "Javier", "Daniel", "Pablo", "Raul", "Oscar", "Victor", "Hugo",
        "Mauricio", "Walter", "Samuel"
    ]
    
    nombres_tutores_mujeres = [
        "María", "Ana", "Rosa", "Carmen", "Laura", "Patricia", "Elena", 
        "Isabel", "Lucía", "Silvia", "Gabriela", "Verónica", "Claudia", 
        "Natalia", "Andrea", "Carolina", "Daniela", "Valeria", "Jimena", "Paola",
        "Sofia", "Camila", "Valentina", "Fernanda", "Alejandra", "Monica",
        "Diana", "Ximena", "Lorena", "Sandra"
    ]

    # USAR LOS VALORES EXACTOS DE LOS CHOICES - LISTAS SIMPLES
    resultados_posibles = [
        ["lectoescritura"],
        ["razonamiento_logico"],
        ["atencion_memoria"],
        ["lectoescritura", "razonamiento_logico"],
        ["psicoeducativa"],
        ["psicopedagogica"],
        ["atencion_memoria", "psicoeducativa"],
        ["multidisciplinaria"],
        ["lectoescritura", "atencion_memoria"],
        ["razonamiento_logico", "psicopedagogica"],
    ]

    programas_posibles = [
        ["lectoescritura"],
        ["razonamiento_logico"],
        ["atencion_disperza"],
        ["lectoescritura", "razonamiento_logico"],
        ["signos_riesgo"],
        ["discapacidad_leve"],
        ["razonamiento_logico", "atencion_disperza"],
        ["lectoescritura", "signos_riesgo"],
        ["atencion_disperza", "discapacidad_leve"],
        ["signos_riesgo", "lectoescritura"],
    ]

    # Evaluaciones requeridas individuales
    evaluaciones_requeridas = [
        "lectoescritura",
        "razonamiento_logico", 
        "atencion_memoria",
        "psicoeducativa",
        "psicopedagogica",
        "multidisciplinaria"
    ]

    # Niveles (PCV, SCP y IFC)
    niveles = ["PCV", "SCP", "IFC"]
    
    # Grados disponibles
    grados = ["1ro", "2do", "3ro", "4to", "5to", "6to"]

    print("🎯 Creando 100 estudiantes adicionales...")
    print("📝 Características:")
    print("   - Departamento: La Paz")
    print("   - Niveles: PCV, SCP e IFC")
    print("   - Mayoría: Atención Directa (80%)")
    print("   - Mayoría: Semestre 2, Gestión 2025 (80%)")

    for i in range(100):
        # Generar datos aleatorios para el estudiante
        apellido_paterno = random.choice(apellidos_estudiantes)
        apellido_materno = random.choice(apellidos_estudiantes)
        
        # Determinar género aleatoriamente
        genero = random.choice(['M', 'F'])
        if genero == 'M':
            nombre = random.choice(nombres_masculinos)
        else:
            nombre = random.choice(nombres_femeninos)
        
        # Generar datos aleatorios con distribución específica
        nivel = random.choice(niveles)
        grado = random.choice(grados)
        colegio = random.choice(colegios_la_paz)
        
        # Mayoría en semestre 2 y gestión 2025 (80%)
        if random.random() < 0.8:  # 80% de probabilidad
            semestre = "2"
            gestion = "2025"
        else:
            semestre = random.choice(["1", "2"])
            gestion = random.choice(["2024", "2025"])
        
        # Mayoría en atención directa (80%)
        if random.random() < 0.8:  # 80% de probabilidad
            modalidad = "directa"
        else:
            modalidad = "indirecta"
        
        # Generar fechas de nacimiento acordes al grado (aproximadamente)
        if grado in ["1ro", "2do"]:
            año_nacimiento = 2015 + random.randint(0, 2)  # 8-10 años
        elif grado in ["3ro", "4to"]:
            año_nacimiento = 2012 + random.randint(0, 2)  # 11-13 años  
        else:  # 5to, 6to
            año_nacimiento = 2010 + random.randint(0, 2)  # 13-15 años
            
        mes_nacimiento = random.randint(1, 12)
        dia_nacimiento = random.randint(1, 28)
        fecha_nacimiento = date(año_nacimiento, mes_nacimiento, dia_nacimiento)
        edad = 2025 - año_nacimiento
        
        # Generar documentos únicos (empezando desde 900000 para no duplicar)
        documento_identidad = f"80{900000 + i}"
        codigo_rude = f"80{900000 + i}{gestion}{str(i).zfill(2)}"

        # Determinar género del tutor basado en el parentesco más probable
        if genero == 'F':
            # Para niñas, es más probable que el tutor sea madre
            nombre_tutor = random.choice(nombres_tutores_mujeres)
            parentesco = "Madre"
            ocupacion = random.choice(["Ama de casa", "Comerciante", "Empleada", "Enfermera"])
        else:
            # Para niños, es más probable que el tutor sea padre
            nombre_tutor = random.choice(nombres_tutores_hombres)
            parentesco = "Padre"
            ocupacion = random.choice(["Empleado", "Conductor", "Comerciante", "Profesor"])
        
        apellido_tutor = random.choice(apellidos_tutores)
        
        # Crear tutor con datos realistas
        tutor = Tutor.objects.create(
            apellido_paterno=apellido_tutor,
            apellido_materno=random.choice(apellidos_tutores),
            nombres=nombre_tutor,
            ci=f"{2000000 + i}LP",  # CI único (empezando desde 2 millones)
            parentesco=parentesco,
            ocupacion=ocupacion,
            zona=random.choice(zonas_la_paz),
            avenida=random.choice(avenidas_la_paz),
            nro_vivienda=f"{random.randint(100, 999)}",
            telefono=generar_telefono(i),
            celular=generar_celular(i),
        )

        # Seleccionar resultados de evaluación (1-2 opciones) - LISTAS SIMPLES
        resultados_evaluacion = random.choice(resultados_posibles)
        
        # Seleccionar programas de apoyo (1-2 opciones) - LISTAS SIMPLES
        programa_apoyo = random.choice(programas_posibles)
        
        # Seleccionar evaluación requerida individual
        evaluacion_requerida = random.choice(evaluaciones_requeridas)

        # Crear estudiante con datos específicos
        Estudiante.objects.create(
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            nombres=nombre,
            pais="Bolivia",
            departamento="La Paz",
            fecha_nacimiento=fecha_nacimiento,
            genero=genero,
            edad=edad,
            documento_identidad=documento_identidad,
            codigo_rude=codigo_rude,
            colegio_procedencia=colegio,
            nivel=nivel,
            grado=grado,
            semestre=semestre,
            maestra_aula=random.choice(maestras_aula),
            gestion_ingreso=gestion,
            zona=random.choice(zonas_la_paz),
            avenida=random.choice(avenidas_la_paz),
            nro_vivienda=f"{random.randint(1, 200)}",
            telefono=generar_telefono(i+1000),  # +1000 para evitar duplicados
            celular=generar_celular(i+1000),    # +1000 para evitar duplicados
            tutor=tutor,
            resultados_evaluacion=resultados_evaluacion,
            evaluacion_requerida=evaluacion_requerida,
            programa_apoyo=programa_apoyo,
            programa_otro="Ninguno",
            modalidad_atencion=modalidad,
        )

        if (i + 1) % 10 == 0:  # Mostrar progreso cada 10 estudiantes
            print(f"✅ Creados {i + 1}/100 estudiantes...")

    print(f"\n🎉 Todos los 100 estudiantes adicionales han sido creados correctamente!")
    print("📍 Características cumplidas:")
    print("   ✅ Departamento: La Paz")
    print("   ✅ Niveles: PCV, SCP e IFC")
    print("   ✅ Mayoría: Atención Directa (80%)")
    print("   ✅ Mayoría: Semestre 2, Gestión 2025 (80%)")
    print("   ✅ Datos aleatorios y realistas")

if __name__ == "__main__":
    crear_100_estudiantes_extra()