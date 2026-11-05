# Revisión integral de Cómo funciona

Fecha: 5 de noviembre de 2026. Repositorio: `iskayApp/como-funciona`.

## Alcance y evidencia inicial

Se revisó la versión `084bc9b686366f1e15e34e76eaf4786f14df3bcc` de `main`, sus 215 archivos fuente y el artefacto real del despliegue GitHub Pages del 5 de noviembre, ejecución `41980691778`. Se contrastaron las 99 fichas de FR con las fuentes editoriales adjuntas. También se consultaron las cuatro guías maestras de las categorías que se preparan para propagación.

La verificación combina código, pruebas de regresión, HTML generado, integración Jekyll, comprobaciones de escritorio/móvil y revisión del sitio publicado. Una comprobación de rutas internas no certifica la reproducción de todos los vídeos externos ni equivale a aprobación editorial.

| Elemento inicial | Resultado comprobado |
| --- | --- |
| Fichas FR | 99: 33 Promotores, 37 Inversores, 29 Colaboradores. |
| Estructura FR | 6 etapas de Promotores, 7 de Inversores, 4 secciones comunes y 4 áreas de Colaboradores. |
| HTML del sitio | 130 páginas. |
| Referencias internas examinadas inicialmente | 5.438, incluyendo 675 referencias con fragmento. |
| Rutas canónicas | 99 únicas y alcanzables desde el recorrido correspondiente. |
| Ensamblaje de marketing | 61 piezas; 185 correspondencias: 93 principales y 92 complementarias; 90 fichas cubiertas. |
| Vídeos FR vinculados | 6 publicaciones; 16 relaciones: 8 principales y 8 complementarias en 9 fichas. |
| Recursos propios | 2 recursos gráficos internos. |
| Categorías nuevas | Donación, Recompensa, Precompra y Acciones en preparación, excluidas de la publicación. |

## Correcciones realizadas

| Incidencia | Corrección y efecto |
| --- | --- |
| La página `404.html` contenía Markdown sin convertir. | Se utiliza HTML válido; aparecen un título real y un enlace funcional para volver al inicio. |
| El catálogo no consideraba las exclusiones de Jekyll. | `public_searchable` respeta `_config.yml`. Una ficha de una carpeta excluida no se ofrece como destino público. |
| La consulta de marketing admitía fichas no publicables. | Solo ofrece enlaces de entradas `public_searchable: true`; la preparación conserva su vista específica. |
| Buscar el código completo `COL-EDU-01 (FR)` podía devolver cero coincidencias. | El buscador incorpora el código con su sufijo de categoría y mantiene los filtros de rol y categoría. |
| El diagnóstico de TikTok evaluaba solo la referencia antigua de una ficha. | Comprueba las 16 relaciones registradas, distingue 6 vídeos únicos y 16 ubicaciones y deduplica la referencia anterior. |
| La deduplicación podía perder una versión de origen ya declarada. | Se conserva la versión únicamente para el par exacto ficha/vídeo que la acredita. Las 15 relaciones sin versión demostrada siguen identificadas como pendientes de esa trazabilidad. |
| La orientación perdía el foco al reemplazar una opción. | Cada transición enfoca la nueva pregunta para continuar con teclado. |
| «Mostrar más resultados» dejaba los nuevos enlaces detrás del foco. | Enfoca el primer resultado nuevo, incluso al agotar la última tanda. |
| El método alternativo de copia podía dejar un campo oculto y perder el foco. | La limpieza y devolución del foco se ejecutan también cuando falla la copia. |
| Siete párrafos de CF-FR-INV-004 estaban marcados como encabezados. | Se corrige solo la sintaxis Markdown. Se conservan todas las palabras, identidad, estado editorial y URL. |
| La portada repetía «Cómo funciona» en el título de la pestaña. | Se presenta una sola vez el título general del sitio. |
| El contenedor inicial de control de ficha apuntaba a un encabezado todavía inexistente. | Incluye su encabezado accesible desde el HTML inicial. |
| La plantilla pedía siempre una acción al promotor. | La acción se refiere al usuario del rol de la ficha y evita atribuirle obligaciones ajenas. |

Se actualizaron las versiones de los recursos JavaScript modificados para facilitar que los navegadores reciban las correcciones.

## Navegación preparada para otros usuarios

Los componentes de contexto, pestañas, portadas de rol y recorrido utilizan ahora el registro común de categorías y roles. Los nombres internos `fr_*` se mantienen como compatibilidad con las páginas, estilos y scripts existentes; ya no fijan obligatoriamente la categoría FR ni construyen las URL a partir de una posición en una lista.

El caso de comprobación aislado utiliza **Donación → Donantes** con una URL deliberadamente distinta del identificador del rol. También comprueba Colaboradores fuera de FR, sin imponerles las cuatro áreas de FR. Los casos de borrador, revisión, archivo, visibilidad privada, `published: false` y categoría en preparación no deben activar enlaces de navegación.

Ese contenido es un fixture sintético de pruebas. No se añade al catálogo público ni constituye contenido funcional de Donación.

## Verificación reproducible

La solicitud de integración ejecuta las comprobaciones de `.github/workflows/validate.yml`; la publicación repite el control del sitio generado antes de subir el artefacto.

- Pruebas Python de catálogo, enlaces, trazabilidad, control editorial, registro de TikTok e integridad del sitio.
- Pruebas Node de búsqueda, orientación, mantenimiento y copia de enlaces, además de revisión sintáctica de JavaScript.
- Construcción Jekyll de las páginas reales y de un fixture aislado con otra categoría y otros roles.
- Comprobación de las 99 rutas, su alcance desde los recorridos y las 16 asociaciones TikTok.
- Auditoría de todos los HTML: destinos internos, fragmentos, identificadores duplicados, referencias accesibles y presencia de un título principal.
- Bloqueo de la publicación si Jekyll ha generado una ficha privada, un borrador, una ficha no publicada o una ficha de una categoría en preparación.
- Navegación a 1280, 390 y 320 píxeles; controles de teclado, ausencia de desbordamiento y navegación básica sin JavaScript.
- Búsqueda local en los tres roles FR, jerarquía de mantenimiento, sus cuatro vistas y fallos controlados de carga.
- Búsqueda local y navegación móvil del fixture Donación/Donantes y Colaboradores.

Los hashes de protección de la fase anterior se actualizan deliberadamente para las correcciones de JavaScript y el ajuste exclusivamente de formato de CF-FR-INV-004. La prueba continúa protegiendo los textos y rutas del conjunto de fichas; las regresiones de comportamiento justifican los cambios al componente común.

El navegador local del entorno de trabajo no pudo iniciarse por una restricción de ejecución. Las pruebas de presentación se ejecutan en GitHub Actions y la experiencia publicada se comprueba en el navegador disponible. Las pruebas simuladas de TikTok no se presentan como una nueva consulta al servicio.

## Estado editorial y asuntos abiertos

| Control | Estado inicial verificado |
| --- | --- |
| Aprobación explícita | 7 fichas: INV001–005 y COL001–002. |
| Pendientes de revisión | 59 fichas. |
| Sin estado editorial explícito | Las 33 fichas de Promotores. No se deduce aprobación del hecho de estar publicadas. |
| Sin `content_version` explícita | 30 fichas de Promotores. |
| Versión de guía no identificada expresamente | Las 99 fichas. Una fecha de modificación no se utiliza como versión aprobada. |
| Fichas sin pieza publicitaria | 9. No constituyen enlaces rotos ni impiden su consulta. |

Las nueve fichas sin asociación publicitaria son **FR-PRO-05, FR-PRO-20, FR-PRO-30, FR-PRO-31, FR-PRO-32, CF-FR-INV-023, CF-FR-INV-026, CF-FR-INV-033 y CF-FR-COL-029**. Se conserva la ausencia hasta verificar una correspondencia editorial real.

### Conciliación editorial de FR

Estas observaciones se registran para revisión en la fuente editorial maestra; no se cambian silenciosamente condiciones funcionales ni se otorgan nuevas aprobaciones.

| Referencia | Observación | Siguiente acción |
| --- | --- | --- |
| FR-PRO-12 | La expresión «cuando corresponda» engloba protocolización e inscripción, mientras la guía específica y FR-PRO-27 separan ambos actos. | Precisar la redacción con la sección de garantía real de la fuente. |
| CF-FR-INV-014 | Se añade «cuando corresponda» al reconocimiento notarial de firmas; las referencias equivalentes de la guía y PRO/COL no lo expresan así. | Conciliar el alcance antes de cerrar la revisión de la ficha. |
| CF-FR-INV-021 | Un encabezado compara confirmación con inicio del reembolso, mientras los párrafos comparan confirmación de inversión y transferencia al promotor. | Alinear encabezado y explicación en la ficha maestra. |
| CF-FR-INV-036 | La aclaración recogida en planificación sobre chat y compartir la iniciativa no aparece desarrollada en la ficha. | Revisar la decisión aprobada y sincronizar su alcance con la fuente maestra. |

## Resultado para la propagación

El documento [PLAN_PROPAGACION_2026-11-05.md](./PLAN_PROPAGACION_2026-11-05.md) identifica los doce recorridos de las otras cuatro categorías, sus fuentes, conflictos documentales, fases y criterios de aceptación. Donación es la siguiente categoría prevista.

La preparación de navegación, buscador, orientación y consulta de enlaces se conserva en el mismo sitio y catálogo. Los registros de ensamblaje de marketing y TikTok continúan siendo específicos de FR: antes de incorporar otros calendarios deberán admitir registros por categoría y resolver la identidad mediante **categoría + código de pieza + código de ficha**, porque un código publicitario puede repetirse entre categorías.

La incorporación pública de cada categoría requiere su clasificación, recorrido propio, inventario, desarrollo, aprobación y comprobación. El trabajo actual deja esa propagación preparada y documentada; no convierte las categorías en preparación en recorridos publicados.
