# Centro de mantenimiento · renovación 2026-11-06

## Resultado

Espacio de consulta con cinco vistas, navegación lateral en escritorio y navegación horizontal en móvil. Panorama resume prioridades editoriales y cobertura multimedia con cifras de las fichas seleccionadas. Las otras cuatro vistas conservan la estructura canónica y los enlaces originales.

- Filtros compartidos de búsqueda, categoría, rol y sección. Las métricas, colas, relaciones de fuentes, biblioteca y diagnóstico respetan la selección. El inventario del servicio TikTok se identifica expresamente como global.
- Panel lateral modal de control de ficha, accesible con teclado, cierre con Escape y retorno al foco y desplazamiento de origen.
- Biblioteca de recursos únicos, fichas y piezas de marketing. Los recursos se deduplican por proveedor e identificador; las relaciones editoriales no se presentan como publicaciones. Búsqueda por código/concepto, proveedor y tipo; resultados paginados.
- Colas por causa: revisión editorial, ausencia de estado, metadatos incompletos, diferencias de versiones, procedencia multimedia desconocida y fichas sin vídeo. Cero diferencias conocidas no significa vigencia verificada.
- Impacto por fuente/sección con paginación y exportación de todas las relaciones seleccionadas.
- URL con vista, filtros, cola, refinamientos, fuente y ficha seleccionada; recarga y navegación atrás/adelante conservan ese contexto. «Copiar vista» copia dicha dirección.
- CSV con la selección completa, incluso si está paginada; comillas, saltos y valores que podrían ejecutarse como fórmulas se escapan.
- Jerarquía nativa sin JavaScript y biblioteca independiente ante fallos del control o informe. El diagnóstico detallado se genera al abrir las secciones.

## Evidencia y procedencia

`maintenance-core.js` concentra las reglas puras de filtrado, recuento, deduplicación, seguridad de enlaces, CSV y vigencia. Los tres módulos de interfaz comparten una lectura en caché del catálogo y eventos de contexto. No se añade una fuente editable ni se altera el contenido de las fichas.

El informe incluye `revision`, tomada de `GITHUB_SHA` o de Git, y `tiktok_inventory.complete`. La interfaz requiere una revisión hexadecimal válida igual a la del catálogo y una fecha comprobable de hasta 36 horas para presentar resultados como actuales. Una fecha futura por más de cinco minutos se rechaza. El inventario requiere además consulta completa y servicio OK; las referencias históricas se conservan sin certificar el total actual.

El despliegue existente genera informe y catálogos desde el mismo checkout. El informe se publica en el artefacto de Pages, sin crear un commit adicional ni modificar el mecanismo de rotación de credenciales.

El control añade `video_count` y `unverified_asset_ids` a cada ficha. `_data/maintenance-public.yml` admite `category_preparation` mediante lista de campos explícita: categoría, título, fase, estado de revisión, fecha, referencia pública y recuentos por rol. Donación muestra IDENTIFICAR preparada para revisión, 40 fichas identificadas que cubren 136 registros documentales; no se añade ninguna ficha de Donación al sitio. Se incorpora el avance remoto `dc20862` antes de publicar esta renovación.

## Alcance preservado

Las 99 fichas, sus códigos, URL, textos, versiones, estados editoriales, relaciones de marketing y registro de TikTok se conservan. La portada, orientación, buscadores públicos y reproductor común no cambian. El diseño usa los iconos y recursos visuales existentes.

El centro no edita datos, aprueba documentos ni sincroniza Drive. Las referencias y metadatos que se añadan deben ser expresamente publicables, porque el repositorio y el sitio son públicos.

## Validación

- Pruebas Python de proyección, listas de campos, fuentes canónicas y diagnóstico TikTok sin red; incluyen inventario parcial, servicio no disponible y revisión del informe.
- Pruebas Node de reglas comunes, fuentes desconocidas, filtrado, deduplicación, CSV y protocolos de enlaces, además de las regresiones existentes.
- Jekyll y auditorías del sitio generado: 99 rutas canónicas alcanzables, navegación en tres roles y 21 secciones, enlaces y fragmentos locales.
- Chromium en 1440, 768, 390 y 320 px: cinco vistas, métricas filtradas, panel contextual, teclado, foco, portapapeles, exportaciones completas, URL persistente, atrás/adelante, biblioteca, colas, paginación y fallo de datos.
- Navegación sin JavaScript; regresiones de portada, buscadores, orientación, navegación por categoría/rol y reproductor en todas las fichas.

Los informes técnicos de las pruebas de navegador son fixtures sintéticos y no certifican la conexión real con TikTok. Capturas y resultados se guardan en `ui-artifacts/` como artefactos de validación. El despliegue genera su propio informe con los servicios configurados.

Esta renovación amplía la [implementación de cuatro vistas del 4 de noviembre](MANTENIMIENTO_CUATRO_VISTAS_2026-11-04.md).
