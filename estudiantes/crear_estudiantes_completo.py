# estudiantes/crear_estudiantes_completo.py

from estudiantes.models import Estudiante, Tutor
from datetime import date

def crear_estudiantes_completo():
    # Zonas reales de La Paz, Bolivia
    zonas_la_paz = [
        "Centro - Sopocachi", "Zona Sur - Calacoto", "Zona Sur - Achumani", 
        "Zona Sur - Obrajes", "Zona Norte - Villa Fátima", "Zona Norte - Miraflores",
        "Zona Este - San Pedro", "Zona Oeste - Alto Obrajes", "Zona Sur - Cota Cota",
        "Zona Norte - Cotahuma", "Zona Centro - San Jorge", "Zona Sur - Irpavi",
        "Zona Sur - Següencoma", "Zona Norte - Sopocachi Bajo", "Zona Este - Munaypata",
        "Zona Oeste - Tembladerani", "Zona Sur - Bolognia", "Zona Norte - Llojeta",
        "Zona Este - Pura Pura", "Zona Oeste - Alto San Pedro"
    ]
    
    avenidas_la_paz = [
        "Av. 16 de Julio", "Av. Arce", "Av. 6 de Agosto", "Av. Camacho", 
        "Av. Mariscal Santa Cruz", "Av. Villazón", "Av. Busch", "Av. Perú",
        "Av. Montes", "Av. Buenos Aires", "Av. Hernando Siles", "Av. del Poeta",
        "Av. Costanera", "Av. del Ejército", "Av. Kollasuyo", "Av. República",
        "Av. Simón Bolívar", "Av. Saavedra", "Av. Landaeta", "Av. Ballivián"
    ]
    
    # Nombres reales de maestras bolivianas
    maestras_aula = [
        "María Elena Vargas", "Ana Luisa Fernández", "Carmen Rosa Torrez", 
        "Patricia Mendez López", "Susana Ríos Quiroga", "Elena Castro Morales",
        "Gabriela Paredes Suárez", "Claudia Rojas Arce", "Verónica Salazar Paz",
        "Jimena Valdez Ribera", "Rosa María Blanco", "Lucía Andrade Camacho",
        "Silvia Peña Ortiz", "Daniela Montesinos", "Carolina Serrano Guzmán",
        "Paola Núñez Castillo", "Andrea Zambrana Rojas", "Natalia Mercado Flores",
        "Valeria Durán Herrera", "Liliana Cordero Miranda"
    ]

    # Colegios de La Paz
    colegios_la_paz = [
        "REPUBLICA DE CANADA", "SANTA ROSA GRANDE", "BOLIVIA", "SANTA CRUZ",
        "COCHABAMBA", "SUCRE", "ORURO", "TARIJA", "BENI", "POTOSI", "LA PAZ",
        "AYACUCHO", "AMERICA", "SAN CALIXTO", "LA SALLE", "SAN ANDRES",
        "MARIANO BAPTISTA", "JUAN XXIII", "SAN IGNACIO", "MEXICO"
    ]

    estudiantes_data = [
        {"apellido_paterno":"CONDE", "apellido_materno":"PAOLA ISABEL", "nombres":"PAOLA ISABEL","fecha_nacimiento":"2014-05-03","edad":11,"documento_identidad":"8073003320","codigo_rude":"807300332020053","colegio_procedencia":"REPUBLICA DE CANADA","genero":"F","nivel":"IFC","grado":"1ro","modalidad_atencion":"directa"},
        {"apellido_paterno":"NINA BLANCO", "apellido_materno":"CHRISTOFER MATIAS","nombres":"CHRISTOFER MATIAS","fecha_nacimiento":"2015-06-26","edad":10,"documento_identidad":"16700378","codigo_rude":"807301782020043","colegio_procedencia":"SANTA ROSA GRANDE","genero":"M","nivel":"IFC","grado":"1ro","modalidad_atencion":"directa"},
        {"apellido_paterno":"MAMANI","apellido_materno":"JULIAN EDUARDO","nombres":"JULIAN EDUARDO","fecha_nacimiento":"2013-09-12","edad":12,"documento_identidad":"80730123","codigo_rude":"807301232020054","colegio_procedencia":"BOLIVIA","genero":"M","nivel":"IFC","grado":"2do","modalidad_atencion":"indirecta"},
        {"apellido_paterno":"QUISPE","apellido_materno":"CARLA MARINA","nombres":"CARLA MARINA","fecha_nacimiento":"2014-11-05","edad":11,"documento_identidad":"80730234","codigo_rude":"807302342020055","colegio_procedencia":"SANTA CRUZ","genero":"F","nivel":"IFC","grado":"2do","modalidad_atencion":"directa"},
        {"apellido_paterno":"HUANCA","apellido_materno":"EDUARDO","nombres":"EDUARDO","fecha_nacimiento":"2013-03-20","edad":12,"documento_identidad":"80730345","codigo_rude":"807303452020056","colegio_procedencia":"COCHABAMBA","genero":"M","nivel":"IFC","grado":"3ro","modalidad_atencion":"directa"},
        {"apellido_paterno":"PAREDES","apellido_materno":"ANA","nombres":"ANA","fecha_nacimiento":"2012-07-15","edad":13,"documento_identidad":"80730456","codigo_rude":"807304562020057","colegio_procedencia":"SUCRE","genero":"F","nivel":"IFC","grado":"3ro","modalidad_atencion":"indirecta"},
        {"apellido_paterno":"MENDOZA","apellido_materno":"JORGE","nombres":"JORGE","fecha_nacimiento":"2011-12-01","edad":14,"documento_identidad":"80730567","codigo_rude":"807305672020058","colegio_procedencia":"ORURO","genero":"M","nivel":"IFC","grado":"4to","modalidad_atencion":"directa"},
        {"apellido_paterno":"VARGAS","apellido_materno":"LUISA","nombres":"LUISA","fecha_nacimiento":"2013-05-18","edad":12,"documento_identidad":"80730678","codigo_rude":"807306782020059","colegio_procedencia":"TARIJA","genero":"F","nivel":"IFC","grado":"4to","modalidad_atencion":"indirecta"},
        {"apellido_paterno":"RODRIGUEZ","apellido_materno":"CARLOS","nombres":"CARLOS","fecha_nacimiento":"2012-09-22","edad":13,"documento_identidad":"80730789","codigo_rude":"807307892020060","colegio_procedencia":"BENI","genero":"M","nivel":"IFC","grado":"5to","modalidad_atencion":"directa"},
        {"apellido_paterno":"GARCIA","apellido_materno":"MARIA","nombres":"MARIA","fecha_nacimiento":"2011-04-11","edad":14,"documento_identidad":"80730890","codigo_rude":"807308902020061","colegio_procedencia":"POTOSI","genero":"F","nivel":"IFC","grado":"5to","modalidad_atencion":"directa"},
        {"apellido_paterno":"LOPEZ","apellido_materno":"DANIEL","nombres":"DANIEL","fecha_nacimiento":"2010-02-25","edad":15,"documento_identidad":"80730901","codigo_rude":"807309012020062","colegio_procedencia":"LA PAZ","genero":"M","nivel":"IFC","grado":"6to","modalidad_atencion":"indirecta"},
        {"apellido_paterno":"CRUZ","apellido_materno":"KAREN","nombres":"KAREN","fecha_nacimiento":"2010-08-17","edad":15,"documento_identidad":"80731012","codigo_rude":"807310122020063","colegio_procedencia":"COCHABAMBA","genero":"F","nivel":"IFC","grado":"6to","modalidad_atencion":"directa"},
        {"apellido_paterno":"MARTINEZ","apellido_materno":"DIEGO","nombres":"DIEGO","fecha_nacimiento":"2011-06-05","edad":14,"documento_identidad":"80731123","codigo_rude":"807311232020064","colegio_procedencia":"SANTA CRUZ","genero":"M","nivel":"IFC","grado":"5to","modalidad_atencion":"directa"},
        {"apellido_paterno":"HERRERA","apellido_materno":"SUSANA","nombres":"SUSANA","fecha_nacimiento":"2012-01-10","edad":13,"documento_identidad":"80731234","codigo_rude":"807312342020065","colegio_procedencia":"LA PAZ","genero":"F","nivel":"IFC","grado":"4to","modalidad_atencion":"indirecta"},
        {"apellido_paterno":"RAMIREZ","apellido_materno":"MIGUEL","nombres":"MIGUEL","fecha_nacimiento":"2013-03-30","edad":12,"documento_identidad":"80731345","codigo_rude":"807313452020066","colegio_procedencia":"BENI","genero":"M","nivel":"IFC","grado":"3ro","modalidad_atencion":"directa"},
        {"apellido_paterno":"SALAZAR","apellido_materno":"LAURA","nombres":"LAURA","fecha_nacimiento":"2014-12-12","edad":11,"documento_identidad":"80731456","codigo_rude":"807314562020067","colegio_procedencia":"TARIJA","genero":"F","nivel":"IFC","grado":"2do","modalidad_atencion":"directa"},
        {"apellido_paterno":"SANTOS","apellido_materno":"RICARDO","nombres":"RICARDO","fecha_nacimiento":"2015-05-05","edad":10,"documento_identidad":"80731567","codigo_rude":"807315672020068","colegio_procedencia":"ORURO","genero":"M","nivel":"IFC","grado":"1ro","modalidad_atencion":"indirecta"},
        {"apellido_paterno":"FERNANDEZ","apellido_materno":"PATRICIA","nombres":"PATRICIA","fecha_nacimiento":"2013-09-09","edad":12,"documento_identidad":"80731678","codigo_rude":"807316782020069","colegio_procedencia":"SUCRE","genero":"F","nivel":"IFC","grado":"3ro","modalidad_atencion":"directa"},
        {"apellido_paterno":"CASTRO","apellido_materno":"JORGE","nombres":"JORGE","fecha_nacimiento":"2012-11-11","edad":13,"documento_identidad":"80731789","codigo_rude":"807317892020070","colegio_procedencia":"POTOSI","genero":"M","nivel":"IFC","grado":"4to","modalidad_atencion":"directa"},
    ]

    def generar_telefono(i):
        return f"2{str(i+1000).zfill(6)}"

    def generar_celular(i):
        prefix = 6 if i % 2 == 0 else 7
        return f"{prefix}{str(i+10000).zfill(7)}"

    # Apellidos comunes para tutores
    apellidos_tutores = [
        "Gonzales", "Rodríguez", "Fernández", "López", "Martínez", 
        "García", "Pérez", "Gómez", "Hernández", "Díaz", "Torres", 
        "Ramírez", "Flores", "Vargas", "Rojas", "Castro", "Romero", 
        "Suárez", "Alvarez", "Ruiz"
    ]
    
    nombres_tutores_hombres = [
        "Juan", "Carlos", "Luis", "Miguel", "José", "Antonio", "Jorge", 
        "Roberto", "David", "Francisco", "Mario", "Pedro", "Fernando", 
        "Ricardo", "Eduardo", "Alberto", "Ramiro", "Sergio", "Andrés", "Diego"
    ]
    
    nombres_tutores_mujeres = [
        "María", "Ana", "Rosa", "Carmen", "Laura", "Patricia", "Elena", 
        "Isabel", "Lucía", "Silvia", "Gabriela", "Verónica", "Claudia", 
        "Natalia", "Andrea", "Carolina", "Daniela", "Valeria", "Jimena", "Paola"
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

    for i, est in enumerate(estudiantes_data):
        # Determinar género del tutor basado en el parentesco más probable
        if est["genero"] == "F":
            # Para niñas, es más probable que el tutor sea madre
            nombre_tutor = nombres_tutores_mujeres[i % len(nombres_tutores_mujeres)]
            parentesco = "Madre"
            ocupacion = "Ama de casa" if i % 3 == 0 else "Comerciante"
        else:
            # Para niños, es más probable que el tutor sea padre
            nombre_tutor = nombres_tutores_hombres[i % len(nombres_tutores_hombres)]
            parentesco = "Padre"
            ocupacion = "Empleado" if i % 2 == 0 else "Conductor"
        
        apellido_tutor = apellidos_tutores[i % len(apellidos_tutores)]
        
        # Crear tutor con datos realistas
        tutor = Tutor.objects.create(
            apellido_paterno=apellido_tutor,
            apellido_materno=apellidos_tutores[(i+5) % len(apellidos_tutores)],
            nombres=nombre_tutor,
            ci=f"{1000000 + i}LP",
            parentesco=parentesco,
            ocupacion=ocupacion,
            zona=zonas_la_paz[i % len(zonas_la_paz)],
            avenida=avenidas_la_paz[i % len(avenidas_la_paz)],
            nro_vivienda=f"{i+100}",
            telefono=generar_telefono(i),
            celular=generar_celular(i),
        )

        # Seleccionar resultados de evaluación (1-2 opciones) - LISTAS SIMPLES
        resultados_evaluacion = resultados_posibles[i % len(resultados_posibles)]
        
        # Seleccionar programas de apoyo (1-2 opciones) - LISTAS SIMPLES
        programa_apoyo = programas_posibles[i % len(programas_posibles)]
        
        # Seleccionar evaluación requerida individual
        evaluacion_requerida = evaluaciones_requeridas[i % len(evaluaciones_requeridas)]
        
        # Cambiar colegio_procedencia a La Paz para todos
        colegio_la_paz = colegios_la_paz[i % len(colegios_la_paz)]

        # Crear estudiante con datos completos - USANDO LISTAS SIMPLES
        Estudiante.objects.create(
            apellido_paterno=est["apellido_paterno"],
            apellido_materno=est["apellido_materno"],
            nombres=est["nombres"],
            pais="Bolivia",
            departamento="La Paz",
            fecha_nacimiento=est["fecha_nacimiento"],
            genero=est["genero"],
            edad=est["edad"],
            documento_identidad=est["documento_identidad"],
            codigo_rude=est["codigo_rude"],
            colegio_procedencia=colegio_la_paz,
            nivel=est["nivel"],
            grado=est["grado"],
            semestre="1",
            maestra_aula=maestras_aula[i % len(maestras_aula)],
            gestion_ingreso="2024",
            zona=zonas_la_paz[(i+3) % len(zonas_la_paz)],
            avenida=avenidas_la_paz[(i+2) % len(avenidas_la_paz)],
            nro_vivienda=f"{i+50}",
            telefono=generar_telefono(i+100),
            celular=generar_celular(i+100),
            tutor=tutor,
            # AQUÍ LA CLAVE: LISTAS SIMPLES, NO OBJETOS JSON
            resultados_evaluacion=resultados_evaluacion,
            evaluacion_requerida=evaluacion_requerida,
            programa_apoyo=programa_apoyo,
            programa_otro="Ninguno",
            modalidad_atencion=est.get("modalidad_atencion", "directa"),
        )

        print(f"✅ Estudiante {i+1}: {est['nombres']} {est['apellido_paterno']}")
        print(f"   Colegio: {colegio_la_paz}")
        print(f"   Evaluación requerida: {evaluacion_requerida}")
        print(f"   Resultados evaluación: {resultados_evaluacion}")
        print(f"   Programas de apoyo: {programa_apoyo}")

    print("\n🎉 Todos los 20 estudiantes y tutores han sido creados correctamente.")
    print("📍 Todos los estudiantes son de La Paz")
    print("📚 Máximo 2 evaluaciones y 2 programas de apoyo por estudiante")
    print("👨‍👩‍👧‍👦 Tutores con datos realistas")

if __name__ == "__main__":
    crear_estudiantes_completo()