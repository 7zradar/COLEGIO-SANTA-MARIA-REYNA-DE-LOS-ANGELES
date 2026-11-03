# Paquete de trabajo APF3 Santa María

Preparado el 02/11/2026. El informe contiene trece páginas de contenido, una portada y dos páginas de referencias. La presentación contiene doce diapositivas con notas y reparto propuesto para 12 minutos más 3 de preguntas.

## Archivos principales
- APF3_Grupo5_SantaMaria.pdf: informe técnico y protocolo de validación inclusiva.
- APF3_Grupo5_SantaMaria.pptx: presentación editable con fuentes en las notas.
- APF3_Grupo5_Matriz_WCAG_y_Validacion.xlsx: 50 criterios, 26 núcleo, 250 registros y hojas vacías de campo.
- APF3_Grupo5_SantaMaria.docx: versión editable del informe.
- APF3_Grupo5_Anexos.zip: instrumentos, evidencias, código y kit Figma.

## Lectura de los anexos
01_Matriz contiene el XLSX. 02_Evidencias incluye JSON y capturas reales. 03_Instrumentos contiene protocolo, consentimiento vacío, registro y cuestionarios, declaración de IA y coevaluación. 04_Figma contiene el importador. 05_Prototipo_web contiene la implementación local v3. 06_Trazabilidad contiene fuentes y datos estructurados del análisis. 07_Editable contiene el DOCX.

## Figma
El equipo confirmó que no dispone de archivo Figma. El kit genera las seis páginas y el flujo visual desde un complemento local. Abrir 04_Figma/LEEME_FIGMA.md. Todavía no se ha ejecutado en la aplicación ni se ha publicado un enlace. El conector Figma también puede usarse después de vincular la cuenta del equipo. Ninguna de estas opciones acredita una sesión Stark sin ejecutarla y conservar sus capturas.

## Prototipo local
Extraer el ZIP. Desde 05_Prototipo_web ejecutar `python server.py --port 8104` con Python 3.10 o posterior. Abrir http://127.0.0.1:8104/ . No abrir index.html directamente, porque las rutas y el guardado requieren el servidor. La base SQLite se inicializa con datos ficticios al iniciar. No se incluyen bases de sesiones previas.

Cuentas del piloto: admin / Admin2026!, ana / Alumno2026!, luis / Alumno2026!, camila / Alumno2026!. El control de acceso se conserva del piloto APF2; las cinco pantallas auditadas incluyen solo el ingreso, no todo el módulo académico posterior.

Para repetir axe abrir una de las cinco rutas con ?auditoria=1 y usar el botón visible de auditoría. La versión axe y su licencia se conservan en el código distribuido. Guardar un nuevo JSON con fecha, versión y estado. No modificar los registros originales. La copia de la línea base pública procede de https://colegio-santa-maria-reyna-angeles.vercel.app/ y su manifiesto de recursos está en Trazabilidad. La v3 de este paquete es local; no se ha reemplazado el despliegue público.

## Cierre de la evaluación
Las sesiones APF3 todavía no se realizaron. Convocar cinco personas de tres perfiles, con al menos dos condiciones reales o ayudas habituales y consentimiento previo. Registrar datos reales y conservarlos anonimizados. Completar Stark, lector, zoom nativo 200%, redistribución y demás verificaciones identificadas. El selector de texto ampliado no equivale a la prueba de zoom.

El uso extenso de IA en este borrador está declarado. La consigna limita ese aporte al 30% y prevé una penalización. El equipo debe revisar la regla, elaborar su análisis propio y registrar contribuciones efectivas. No se garantiza una nota ni se presenta el paquete como validación inclusiva terminada.
