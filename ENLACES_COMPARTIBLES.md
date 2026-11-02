# Enlaces compartibles automáticos · Cómo funciona

## Propósito

Cada ficha canónica es el punto de referencia de un concepto funcional. Marketing, soporte y los usuarios pueden compartir la ficha completa, ir a un elemento multimedia dentro de ella y acceder al archivo o publicación original del recurso. **No se redactan enlaces manualmente.**

El patrón es común para categorías y roles actuales y futuros. No tiene condiciones exclusivas de Promotores ni de Financiamiento Reembolsable.

## Tres destinos

1. **Ficha**: se deriva de `permalink` con `url` y `baseurl` configurados en Jekyll. El componente aparece automáticamente en cualquier ficha con `code` y `permalink`.
2. **Multimedia dentro de la ficha**: URL canónica más `#media-<id>`. Un recurso visible debe contar en el cuerpo HTML con el atributo `id="media-<id>"`, donde el `id` proviene del bloque `media` del front matter.
3. **Original**: primero `original_url` o `share_url` o `url` explícitos y válidos; después se construye desde `provider: youtube` + `video_id`, o a partir de `src` interno o externo. Para TikTok se requiere `share_url`, `original_url` u otra URL real verificable; **un video_id sin cuenta/URL no basta para construir un destino fiable**.

Solo se muestran recursos multimedia con `status: approved` y `visibility` distinto de `private`. Si los metadatos no permiten identificar el recurso original, el botón se muestra deshabilitado. No se inventan enlaces.

## Ejemplo interno (ficha FR-PRO-09)

```yaml
media:
  - id: fr-pro-09-flujo-pagos
    type: animation
    storage: internal
    src: /assets/financiamiento-reembolsable/promotores/fr-pro-09/flujo-pagos.svg
    status: approved
    derived_from_version: 1
```

Dentro del contenido:

```html
<figure id="media-fr-pro-09-flujo-pagos" class="media-block">
  <!-- Imagen u otro recurso -->
</figure>
```

Los tres destinos se generan desde la URL de la ficha y el bloque anterior. En GitHub Pages, la URL interna incluye automáticamente el prefijo `/como-funciona`.

## Ejemplo de YouTube

```yaml
media:
  - id: fr-pro-09-video-explicativo
    type: video
    provider: youtube
    storage: external
    video_id: "ID_REAL_DEL_VIDEO"
    status: approved
    visibility: public
    derived_from_version: 1
```

La ubicación visual debe conservar el ancla `media-fr-pro-09-video-explicativo`. El enlace original se deriva del identificador de YouTube; no es necesario escribir una URL completa.

## Ejemplo de TikTok

```yaml
media:
  - id: fr-pro-09-tiktok-explicativo
    type: video
    provider: tiktok
    storage: external
    video_id: "ID_REAL_DEL_VIDEO"
    share_url: "https://www.tiktok.com/@cuenta/video/ID_REAL_DEL_VIDEO"
    status: approved
    visibility: public
    derived_from_version: 1
```

`share_url` es un metadato de publicación que debe proceder del proveedor o de la publicación autorizada. En este ejemplo es ilustrativo, no una publicación existente.

## Catálogo para marketing y mantenimiento

En cada despliegue se genera automáticamente `mantenimiento/share_catalog.json` usando `scripts/build_share_catalog.py`. Contiene las fichas por `code`, `category`, `role`, `stage`, `content_version`, URL canónica y recursos con sus enlaces internos y originales. Este inventario es legible por otros sistemas para alimentar futuras vistas de marketing, planificación editorial y análisis de impacto.

La identidad de la ficha es `code`, su destino público es `permalink` y cada recurso conserva su `id` único. **Nunca cambiar esos valores por una corrección de título o reemplazo de archivo.** Para cambiar proveedor o fuente, ajustar solo los metadatos del origen; la URL con ancla permanece estable.

La comprobación automática de la rama valida códigos/URLs no duplicados, identificadores seguros y únicos y anclas presentes. Enlaces inexistentes o privados no deben compartirse. No se registra contenido sensible en el catálogo público.

## Uso práctico

Marketing podrá seleccionar una ficha por su código, consultar el enlace canónico y compartir la multimedia o publicación original cuando exista. La ficha continúa respaldada por la guía aprobada; los videos y piezas derivadas conservan la relación `derived_from_version` para identificar cambios que necesitan revisión.

La implementación disponible en este repositorio es **pública y de lectura/copia**. No sustituye todavía a un gestor editorial, ni publica por sí misma piezas nuevas en YouTube o TikTok.
