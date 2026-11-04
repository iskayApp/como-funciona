# Cómo funciona · iskay.app

Documentación pública de iskay.app para explicar sus categorías, recorridos y procedimientos de forma clara, accesible desde móvil y mantenible mediante control de versiones.

## Principio de arquitectura

La categoría es la unidad funcional principal. La navegación se organiza por categoría, rol, etapa y ficha.

Las cinco categorías de Ideas son Donación, Recompensa, Precompra, Inversión en Acciones y Financiamiento Reembolsable.

## Alcance actual

- **Financiamiento Reembolsable** incorpora tres recorridos: **Promotores (33 fichas y seis etapas), Inversores (37 fichas y siete etapas) y Colaboradores (29 fichas en base común y cuatro áreas)**.
- En total existen **99 fichas publicadas**: 33 de Promotores y 66 fichas nuevas para Inversores y Colaboradores. Las que aún no cuentan con aprobación editorial muestran un aviso visible.
- Todas las fichas disponen de URL canónica y los recorridos tienen navegación por rol y etapa.
- Las demás categorías conservan su estructura base, pero todavía no forman parte de la publicación pública activa.
- El apartado Recursos permanece fuera del alcance actual.

## Criterios editoriales

La guía aprobada es la fuente de verdad del contenido funcional. Las fichas simplifican y explican sin inventar requisitos, modificar montos ni crear obligaciones nuevas.

Google Drive funciona como fuente maestra editorial y este repositorio actúa como espejo técnico y publicable. Cada ficha conserva categoría, rol, etapa, código, fuente, versión de guía, estado, fecha de revisión y URL estable.

## Capa multimedia

Las fichas admiten una capa multimedia complementaria y extensible. No está limitada a imágenes o videos: el modelo puede incorporar diagramas, animaciones, audio, contenidos interactivos, recursos embebidos, documentos, descargables, galerías, modelos 3D y futuros formatos sin reorganizar la arquitectura.

El texto continúa siendo la fuente principal de cada ficha. Los recursos multimedia no pueden introducir reglas distintas de las respaldadas por la documentación aprobada y deben disponer de comportamiento accesible y fallback.

La especificación se encuentra en [MULTIMEDIA.md](./MULTIMEDIA.md).

## Enlaces compartibles y catálogo para marketing

Las fichas disponen de un componente común para copiar su URL canónica y, cuando tengan multimedia aprobada, el enlace directo al recurso dentro de la ficha y el enlace al archivo o publicación original. Los destinos se construyen automáticamente a partir de los metadatos; no se escriben a mano ni dependen de un rol específico.

En cada despliegue se genera `mantenimiento/share_catalog.json`, con fichas y recursos ordenados por categoría, rol, etapa y código, para facilitar la distribución editorial. **El Centro de mantenimiento** (`/mantenimiento/`) incluye una consulta de concepto/título/código, categoría y rol, que muestra las piezas publicables asociadas y permite copiar los tres enlaces disponibles sin trabajar con JSON. Las piezas de distribución que no están insertadas en la ficha no reciben anclas ficticias. El ensamblaje editorial de FR aprobado el 4 de noviembre de 2026 se conserva en `_data/fr_ensamblaje_marketing.json`: relaciona 61 piezas con 90 fichas mediante 185 correspondencias principales/complementarias. El catálogo y el buscador del mantenimiento muestran esas relaciones sin requerir publicaciones previas; los recursos efectivos siguen vinculándose únicamente mediante `marketing_pieces` y `asset_ids` verificados. Los activos sin código técnico continúan identificados por separado. Ver [ENLACES_COMPARTIBLES.md](./ENLACES_COMPARTIBLES.md).


## TikTok oficial enlazado a fichas

El registro `_data/fr_tiktok_publicaciones.json` contiene exclusivamente vídeos públicos de la cuenta oficial **@iskay.app** comprobados en el inventario autenticado de TikTok. Se relacionan con los códigos publicitarios del ensamblaje editorial aprobado, no mediante coincidencias de títulos o números. Seis vídeos de Financiamiento Reembolsable aportan ocho ubicaciones principales y ocho enlaces complementarios, distribuidos en nueve fichas canónicas.

El componente `_includes/fr-tiktok-videos.html` muestra los reproductores de TikTok en las fichas principales bajo interacción voluntaria, y enlaza la publicación original desde las complementarias. El generador común incorpora los vídeos verificables en `media` y `distribution`, y los agrupa bajo `marketing_pieces` sin alterar el contenido funcional, los códigos ni las URL de las fichas. Si TikTok retira una publicación o cambia el permiso de acceso, el control técnico lo registra; no se crean nuevos enlaces por inferencia.

## Orientación guiada (sin datos personales)

La portada ofrece **«¿No sabes por dónde empezar? Recibir orientación»** como entrada secundaria, sin alterar el buscador público. Una secuencia breve de preguntas con botones permite identificar la categoría, el rol, la etapa y la explicación concreta. La salida dirige **únicamente a la URL canónica** de una ficha pública del catálogo compartido `mantenimiento/share_catalog.json`. No existe otro catálogo ni se copian contenidos entre fichas.

La orientación no es un formulario de registro: no requiere nombre, correo, teléfono, identificación, importes ni información económica; no crea perfiles, no guarda respuestas y no envía las selecciones a un servidor. El único acceso de red es la lectura del catálogo público ya utilizado por el buscador. Se puede volver atrás, comenzar de nuevo o cerrar la orientación en cualquier momento.

La cobertura se limita a recorridos con fichas efectivamente publicadas. Si una modalidad o rol no tiene fichas públicas, se informa con claridad y se facilita el acceso al buscador, **sin recomendar fichas de otro rol como equivalentes**. Los nuevos recorridos se harán accesibles al publicarse sus fichas con metadatos correctos en el mismo catálogo.

## Buscador público

La portada de `Cómo funciona` incluye una barra de búsqueda principal por concepto, pregunta, título o código de ficha. Al introducir un término aparecen resultados compactos; después se pueden desplegar filtros de categoría y rol. Las fichas enlazan directamente a la URL canónica, sin mostrar códigos de marketing ni campos de mantenimiento. La cabecera ofrece un icono de lupa para acceder al buscador desde cualquier ficha, sin duplicar títulos en móviles.

La interfaz pública reutiliza `mantenimiento/share_catalog.json` **sin un segundo catálogo** y solo muestra título, categoría, rol, etapa y código de ficha. No expone en los resultados códigos de piezas publicitarias, enlaces originales de marketing, versiones, estados internos o verificaciones técnicas. Solo se ofrecen fichas marcadas como `public_searchable` y con URL del mismo sitio.

Por defecto no se presenta un listado completo: hay resultados después de escribir o seleccionar filtros. La vista muestra seis coincidencias por tanda, con opción de ampliar. La navegación por las seis etapas se conserva como alternativa, incluso si falla la carga del buscador.

## Publicación

El sitio se publica mediante GitHub Pages:

https://iskayapp.github.io/como-funciona/

Las fichas permiten acceso directo sin iniciar sesión ni descargar archivos y están preparadas para lectura desde móvil.

Durante esta fase de prueba pública, el sitio mantiene `noindex: true` para evitar indexación en buscadores hasta que se apruebe su integración definitiva.

## Estado

- Repositorio: **público**.
- Rama principal: `main`.
- GitHub Pages: **activo**.
- Financiamiento Reembolsable: **99 fichas en tres roles · PRUEBA PÚBLICA** (59 nuevas pendientes de revisión editorial).
- Promotores: 6 etapas; Inversores: 7 etapas; Colaboradores: base común y cuatro áreas de colaboración.
