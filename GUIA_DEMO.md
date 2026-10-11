# Recorrido de demostración APF2

Inicia `python server.py` y abre `http://127.0.0.1:8000/`. Usa únicamente datos ficticios. El portal es un rediseño académico independiente y la intranet no pertenece a la institución.

## Portal público

1. Presenta Inicio y su identidad: escudo, fotografías institucionales de archivo, jerarquía y accesos para familias.
2. Abre Primaria. Identifica aprendizaje significativo, creatividad y acompañamiento familiar. Explica la síntesis del contenido original.
3. Usa “Consultar por Primaria”; el motivo aparece preseleccionado en Contacto.
4. Envía el formulario vacío y muestra los errores junto a cada campo y el foco en el primero.
5. Completa nombre y correo ficticios, un mensaje de al menos 12 caracteres y el consentimiento de demostración. Registra la consulta y anota su código.
6. Abre Galería, filtra Primaria, amplía una fotografía y cierra con Escape. Las imágenes son de archivo; no representan actividades de 2026.
7. Reduce la ventana y comprueba el menú y la lectura en móvil.

## Calificación de principio a fin

1. Ingresa a Intranet con `admin / Admin2026!`.
2. En Calificaciones selecciona Ana Torres, Matemática, Bimestre 3 y Evaluación bimestral.
3. Muestra que una nota fuera de 0–20 se rechaza. Registra 19 y guarda.
4. Comprueba la confirmación y el dato en la tabla. El registro identifica la evaluación y el bimestre.
5. Cierra sesión e ingresa con `ana / Alumno2026!`.
6. Abre Mis calificaciones y Bimestre 3. La nota 19 debe aparecer en Matemática, Evaluación bimestral.
7. Descarga el reporte CSV. El promedio mostrado es referencial y utiliza solo evaluaciones registradas.

Puedes usar una ventana privada para mantener otra sesión independiente. Los cambios se comparten en el servidor, aunque se use otro navegador conectado al mismo servidor local. Para cambiar de rol en la misma ventana hay que cerrar sesión.

## Actividad y consulta

1. Como Ana, abre Mis actividades y la actividad de Matemática.
2. Escribe una respuesta ficticia de al menos 10 caracteres. Envía y comprueba “Entregada”. Vuelve a abrirla para demostrar la edición.
3. Ingresa como administrador y abre Actividades. Revisa las entregas de ese curso: debe aparecer la respuesta de Ana con su fecha.
4. Abre Consultas. Localiza el código generado en el portal, lee la solicitud y cambia el estado a Atendida.
5. Explica que se registra la atención en la muestra; no se envía correo al colegio ni a la familia.

## Gestión por aula

El administrador puede registrar un estudiante ficticio con su cuenta, editar o desactivar su acceso, crear y editar cursos, agregar bloques al horario y publicar actividades. Un bloque no puede superponerse con otro del mismo aula o salón. Los cursos y actividades de Primaria no se muestran a Camila, que pertenece a Secundaria.

Publica un comunicado dirigido a Secundaria, comprueba que Camila lo vea y que Ana no lo reciba. Los comunicados “Todos” llegan a ambos niveles.

## Evidencia técnica y resultados con usuarios

Las capturas en `qa-output/` muestran la revisión técnica realizada el 11 de octubre de 2026, incluyendo una nota 19 guardada y consultada. En la base de demostración quedan esa nota, una entrega de texto y una consulta ficticia que puedes usar como ejemplo.

La comprobación técnica no sustituye el experimento APF2. Registra participantes anonimizados, tareas, tiempos, errores, ayuda recibida y respuestas SUS reales. Actualiza el DOCX y PPTX para que describan esta versión. Conserva el aviso de entorno independiente y no presentes los datos de muestra como expedientes reales.
