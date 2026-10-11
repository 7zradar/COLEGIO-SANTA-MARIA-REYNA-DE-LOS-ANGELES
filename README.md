# Santa María Reyna de los Ángeles

Portal público e intranet académica del proyecto APF2 Grupo 5. Rediseño independiente basado en el sitio público del colegio de La Perla, Callao. La información académica, las cuentas, los cursos, docentes, notas y actividades de la intranet son ficticios.

## Iniciar el proyecto

Necesitas Python 3.10 o posterior. No requiere instalar bibliotecas, Node.js ni una base de datos externa.

Abre una terminal en esta carpeta y ejecuta:

```powershell
python server.py
```

También puedes ejecutar `./iniciar.ps1` desde PowerShell. Mantén abierta la terminal mientras uses el proyecto.

Abre [el portal local](http://127.0.0.1:8000/) o [la intranet](http://127.0.0.1:8000/intranet.html). Si el puerto está ocupado, ejecuta `python server.py --port 8001` y usa esa dirección. Ctrl+C detiene el servidor.

Abrir index.html directamente permite ver el portal, pero las consultas y la intranet requieren server.py. `python -m http.server` no implementa la API de esta versión.

## Cuentas de demostración

| Perfil | Usuario | Contraseña | Aula |
| --- | --- | --- | --- |
| Administrador | admin | Admin2026! | Coordinación |
| Estudiante | ana | Alumno2026! | 5.º A de Primaria |
| Estudiante | luis | Alumno2026! | 5.º A de Primaria |
| Estudiante | camila | Alumno2026! | 1.º A de Secundaria |

Registrar un estudiante desde administración también crea su cuenta con el usuario y contraseña de demostración elegidos. Desactivarlo impide el acceso; su historial se conserva.

## Qué cambió

El portal conserva las siete rutas: Inicio, Nosotros, Inicial, Primaria, Secundaria, Galería y Contacto. Usa el escudo y fotografías obtenidos del sitio del colegio, una identidad visual compartida, navegación adaptable, enlaces por nivel, preguntas frecuentes y galería con filtros y ampliación. El diálogo de imágenes permite cerrar con Escape y devuelve el foco al botón de origen.

La intranet incluye inicio de sesión, dashboard por rol, cursos por aula, horario semanal, evaluaciones por bimestre, entrega de respuestas a actividades y comunicados por nivel. El administrador registra y edita estudiantes y cursos, gestiona horarios, actualiza calificaciones, publica actividades y comunicados, revisa respuestas y atiende consultas. Un reporte CSV permite descargar las notas del bimestre seleccionado.

Las consultas del portal se guardan con un código de seguimiento y aparecen en la bandeja administrativa. No se envía correo ni se contacta al colegio. Usa datos ficticios.

## Persistencia y arquitectura

Frontend: HTML, CSS y JavaScript sin compilación. Backend: servidor HTTP de Python y SQLite. Se eligió la biblioteca estándar para que el equipo pueda ejecutar el piloto sin instalar dependencias; no se utiliza FastAPI.

`data/santamaria.sqlite3` se crea al primer inicio. Los cambios son compartidos por las sesiones conectadas a este servidor y sobreviven al reinicio. No dependen de localStorage. Las sesiones se mantienen en memoria durante dos horas y se cierran al reiniciar el servidor.

Las contraseñas se almacenan mediante PBKDF2 con sal individual; la sesión utiliza cookie HttpOnly y SameSite, los cambios autenticados requieren token CSRF y la API aplica permisos por rol. El estudiante recibe únicamente los datos de su aula y sus propias notas y entregas. La API valida notas de 0 a 20, fechas, correspondencia entre curso y aula y conflictos de horario. Los cambios académicos generan un registro de auditoría.

Es un piloto local con cuentas públicas de demostración. El servidor escucha solo en 127.0.0.1. No está preparado para operar con datos reales: una implementación institucional necesitaría un servidor de producción, HTTPS, gestión de credenciales, copias de seguridad, políticas de protección de datos y revisión profesional del acceso.

Para recuperar la muestra inicial, detén el servidor, conserva una copia de `data/santamaria.sqlite3` y mueve el archivo a otra ubicación. Al iniciar de nuevo se crea una muestra nueva. No sobrescribas la base si deseas conservar los cambios de tu demostración.

## Verificación realizada

```powershell
python verify_project.py
node --check app.js
node --check intranet.js
```

Las 13 pruebas de integración pasaron el 11 de octubre de 2026. Utilizan una base temporal y verifican autenticación, sesión, acceso por rol, privacidad del estudiante, actualización de notas entre sesiones independientes, persistencia SQLite, validaciones, horarios, cuentas nuevas e inactivas, entregas, comunicados segmentados, seguimiento de consultas, auditoría y cierre de sesión.

Se revisó el proyecto en el navegador en escritorio y móvil de 390 × 844. Se comprobó la navegación pública, las siete páginas sin desbordamiento horizontal, las fotografías, el menú móvil, filtros y cierre de la galería con restauración de foco, validación del contacto, consulta guardada, registro de nota 19 y lectura posterior como estudiante, entrega de tarea y horario semanal. Las capturas técnicas están en `qa-output/`; no son resultados de pruebas con participantes ni evidencia de conformidad WCAG completa.

## Documentación y entrega APF2

Consulta `GUIA_DEMO.md` para el recorrido de sustentación. `assets/FUENTES.md` identifica los recursos institucionales.

Los DOCX y PPTX originales describen la versión anterior basada en selección de perfil y localStorage. Deben actualizarse antes de entregar para reflejar autenticación de demostración, persistencia en SQLite, consultas guardadas y fotografías de archivo. No se modificaron esos documentos en esta tarea.

Este trabajo mejora el producto; no garantiza una nota 20/20. Las mediciones con participantes, SUS y capturas comparables antes/después deben obtenerse realmente. No se fabricaron resultados.

El proyecto se entrega local. Para una URL pública con toda la intranet necesitas alojar el servidor Python y conservar la base SQLite en almacenamiento persistente. GitHub Pages o Netlify Drop solo servirían la parte estática y no ejecutarían esta intranet. No existe un despliegue público verificado.
