# Santa María Reyna de los Ángeles

Portal institucional e intranet académica del Grupo 5. El APF3 incorpora mejoras de accesibilidad sobre la experiencia pública utilizada en el APF2. Es un proyecto académico independiente con cuentas y datos ficticios.

## Ejecutar el sistema

Se necesita Python 3.10 o posterior. Desde la raíz del repositorio:

```powershell
python server.py
```

Abrir [el portal](http://127.0.0.1:8000/) o [el ingreso](http://127.0.0.1:8000/intranet). También se puede ejecutar `./iniciar.ps1`. Mantener la terminal abierta. Para otro puerto, usar `python server.py --port 8001`.

Las rutas y las operaciones requieren este servidor. Abrir el archivo HTML directamente o usar un servidor exclusivamente estático no ejecuta la API de contacto ni la intranet.

## Mejoras del APF3

- Contraste de numeración y bordes, enlaces subrayados e indicador visible de foco.
- Preferencias de alto contraste y texto ampliado.
- Nombres accesibles coherentes con sus etiquetas visibles.
- Modal de galería con navegación contenida y retorno del foco.
- Títulos descriptivos y orientación al cambiar de ruta.
- Errores asociados a campos, resumen de recuperación y comunicación de estados.
- Revisión de consulta antes del guardado, retorno a edición y confirmación con código.
- Declaración de accesibilidad parcial en `/accesibilidad`.

Los cambios de apariencia y comportamiento están en `accessibility.css` y `accessibility.js`. El portal usa los recursos compilados de la experiencia pública del APF2 guardados en `assets/index-*.js` y `assets/index-*.css`. Esta copia conserva las fotografías y recursos del proyecto. Los archivos históricos `app.js` y `styles.css` permanecen en el repositorio como referencia de la implementación anterior; el punto de entrada público actual es `index.html`.

La intranet posterior al ingreso conserva los módulos de estudiantes, cursos, horario, evaluaciones, actividades, entregas y comunicados del piloto Python/SQLite. El administrador puede actualizar una nota y el estudiante visualizarla desde otra sesión. Las consultas de demostración se guardan en la bandeja administrativa local y no se envían al colegio.

## Cuentas de demostración

| Perfil | Usuario | Contraseña |
| --- | --- | --- |
| Administrador | admin | Admin2026! |
| Estudiante | ana | Alumno2026! |
| Estudiante | luis | Alumno2026! |
| Estudiante | camila | Alumno2026! |

`data/santamaria.sqlite3` se inicializa al arrancar y conserva los cambios locales. Esta carpeta está excluida de Git. Las sesiones se mantienen en memoria durante dos horas. Se mantienen cookies HttpOnly/SameSite, protección CSRF en operaciones autenticadas y control de acceso por rol. El servidor escucha solo en 127.0.0.1 y está destinado a demostraciones con datos ficticios.

## Informes y anexos

La carpeta [avance informe 3](avance%20informe%203/) contiene el PDF, DOCX, PPTX, XLSX y los ZIP con las evidencias e instrumentos del APF3. El historial de Git conserva la versión APF2.

El informe distingue auditoría técnica de validación con participantes. La conformidad es parcial. El equipo aún debe ejecutar las sesiones inclusivas y verificar el archivo Figma compartido, Stark, lector y zoom nativo. Los datos de participantes del APF2 conservan su carácter de línea base. El apoyo de IA está declarado y debe revisarse frente al límite de la consigna.

## Verificación

```powershell
python verify_project.py
node --check accessibility.js
node --check intranet.js
```

`verify_project.py` utiliza una base temporal para comprobar las rutas públicas, autenticación, permisos, notas, validaciones, horarios, actividades, comunicados, consultas y cierre de sesión. Para repetir axe-core 4.14.0, abrir una ruta con `?auditoria=1` y usar el botón de auditoría. Los JSON originales y las limitaciones están en los anexos. Cero incidencias automáticas no certifica conformidad AA.

## Despliegue

La URL de referencia del APF2 es [el portal publicado en Vercel](https://colegio-santa-maria-reyna-angeles.vercel.app/). Esta subida actualiza el repositorio. La API Python y la persistencia SQLite necesitan un entorno que ejecute el servidor y conserve su almacenamiento; una publicación exclusivamente estática no implementa esas operaciones. Verificar cualquier integración automática de despliegue por separado.

`assets/FUENTES.md` documenta los recursos institucionales. El proyecto y los datos de demostración no constituyen un canal oficial del colegio.
