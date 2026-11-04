# Base general de Cómo funciona — fase 1

## Alcance autorizado

Generalizar la portada, ampliar el menú por categorías y completar la jerarquía de mantenimiento. FR se utiliza como caso de comprobación. No desarrollar Donación todavía y no realizar revisión editorial.

## Estructura implementada

- Portada general: buscador existente, exploración por categoría y orientación breve existente.
- Registro de navegación único `_data/categories.yml`, compartido por portada, menú y mantenimiento. Contiene categorías, disponibilidad y rutas de roles; no duplica las fichas.
- Disponibilidad efectiva: etiqueta `available` + portada existente + fichas publicables reales. Las categorías en preparación no generan enlaces a recorridos vacíos.
- Mantenimiento nativo: categoría → rol → sección → ficha, con las 99 fichas obtenidas directamente de las páginas canónicas.
- Diagnóstico técnico: misma jerarquía, sin mezclar secciones homónimas entre roles o categorías. Los informes antiguos sin categoría/rol se resuelven mediante su URL canónica y el registro común.
- Se conservan búsqueda de piezas, enlaces compartibles, recursos propios/sociales/externos y pendientes de vinculación. El estado técnico no implica aprobación editorial.

## Conservación

Base: `bb4b62984b92d20e8981ff5b24db3743f4ef2112`.
La carpeta `ideas` y los scripts existentes de buscador público, orientación y consulta de marketing se protegen mediante sus hashes en las pruebas. No se modifican textos, códigos, permalinks, versiones, aprobaciones ni avisos de las fichas FR. No se cambian documentos en Drive ni la guía funcional.

## Validación

Las pruebas existentes de FR continúan activas. Se añaden comprobaciones de configuración, protección de fuentes, aislamiento por categoría/rol/sección, navegación a 1280/390/320 px y funcionamiento sin JavaScript. El diagnóstico se prueba en navegador con un reporte controlado; esto no certifica servicios externos como TikTok. Las capturas y resultados se guardan como artefactos de GitHub Actions.

## Límites y orden siguiente

El mantenimiento continúa siendo un panel público de consulta, no un administrador autenticado. No introducir datos privados ni notas confidenciales en el catálogo servido públicamente. No se incorporan edición ni aprobación automática.

Después de validar esta base, Donación seguirá el orden CLASIFICAR → ORGANIZAR → IDENTIFICAR → DESARROLLAR a partir de su propia guía vigente. No copiar etapas ni obligaciones de FR. Las pruebas de snapshot de esta fase se actualizarán deliberadamente al autorizar la siguiente ampliación.
