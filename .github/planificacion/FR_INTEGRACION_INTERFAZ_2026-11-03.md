# Integración de interfaz de Financiamiento Reembolsable

Solicitud del 3 de noviembre de 2026: avanzar con una presentación homogénea, amigable y fácil de explorar de Promotores, Inversores y Colaboradores; añadir menú desplegable. La revisión editorial se realizará después.

## Implementación

- Menú compartido «Explorar» con acceso a FR y sus tres roles; disponible en la cabecera.
- Portada con tres entradas equivalentes, sin favorecer exclusivamente el recorrido de Promotores.
- Un mismo componente para los índices de rol, con secciones desplegables y acceso directo a cada ficha canónica.
- Cambio de rol, enlace de regreso al recorrido y menú «Ir a una sección» en las fichas y páginas de etapa.
- Breadcrumbs con categoría, rol y sección; presentación común de las listas de etapas.
- Colaboradores conserva 11 fichas de base común y 18 en sus cuatro áreas, sin imponer un itinerario único.
- Títulos, recuentos y destinos de navegación generados desde los metadatos de las páginas canónicas; no existe un segundo catálogo de fichas.
- Menús nativos utilizables sin JavaScript, mejoras de cierre con Escape/clic exterior, foco visible, enlace de salto y adaptación móvil.

## Invariantes

No se modifica ninguna de las 99 fichas, sus códigos, permalinks, multimedia, fuentes, contenidos ni estados editoriales. Se mantienen 59 avisos pendientes, el buscador, orientación sin datos personales, mantenimiento y noindex. La guía funcional y los documentos de Drive no cambian.

## Comprobación

La validación de PR conserva las pruebas existentes, comprueba las 99 páginas renderizadas y sus enlaces, y realiza navegación real con Chromium a 1280, 390 y 320 píxeles, además de teclado y JavaScript desactivado. Las capturas e informe se guardan en el artefacto fr-navigation-ui.
