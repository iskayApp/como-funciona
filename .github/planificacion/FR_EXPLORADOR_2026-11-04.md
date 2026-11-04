# FR · Continuidad de la integración: exploración dentro de cada rol

Solicitud: continuar la interfaz homogénea de Promotores, Inversores y Colaboradores. Las revisiones editoriales se mantienen para después.

## Alcance
- Búsqueda local por título o código canónico, sin distinguir mayúsculas ni tildes.
- Desplegable de secciones generado desde la navegación existente, sin catálogo paralelo.
- Colaboradores conserva dos grupos: Base común y Áreas de colaboración; los cuatro nombres oficiales se toman de los títulos vigentes.
- Búsqueda y sección pueden combinarse. Se muestran recuentos y se abren las coincidencias.
- Limpiar filtros restaura las secciones abiertas antes de filtrar. El estado vacío ofrece acceso al buscador general.
- Sin solicitudes de red, registro, cookies, almacenamiento local ni analítica. Sin JavaScript, se ocultan los controles y sigue disponible la navegación nativa.

## Preservación
Los 99 archivos de fichas canónicas, sus códigos, textos, URLs, estados editoriales y recursos multimedia no se modifican. No se modifica Drive ni la guía funcional. El buscador general, orientación guiada, mantenimiento, menú Explorar y navegación entre roles continúan sin cambios.

## Validación reproducible
El flujo de validación existente añade `node --check assets/js/fr-explorer.js` y `python scripts/smoke_fr_explorer.py _site`, después de las pruebas anteriores. El nuevo test usa el sitio Jekyll real y verifica los tres roles a 1280, 390 y 320 px: código, tildes, secciones, filtros combinados, cero resultados, limpieza, teclado, preservación del DOM y ausencia de almacenamiento. También comprueba navegación sin JavaScript. Los resultados y capturas se adjuntan al artefacto `fr-navigation-ui`.
