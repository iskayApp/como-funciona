# Arquitectura multimedia · Cómo funciona

Esta especificación define la capa multimedia extensible de las fichas de **Cómo funciona**.

## Principio

El contenido textual de cada ficha sigue siendo la fuente principal y canónica de la explicación. Los recursos multimedia complementan, aclaran o demuestran el contenido, pero no deben introducir requisitos, montos, obligaciones o reglas que no estén respaldados por la fuente aprobada.

La arquitectura multimedia no se limita a imágenes o videos. Debe poder incorporar nuevos tipos de recursos sin modificar la estructura general de las fichas.

## Tipos de recursos admitidos

La propiedad `type` es abierta y extensible. Como catálogo inicial se contemplan:

- `image`
- `video`
- `diagram`
- `animation`
- `audio`
- `interactive`
- `embed`
- `document`
- `downloadable`
- `gallery`
- `model-3d`
- `other`

La incorporación futura de un nuevo tipo no exige cambiar el modelo general; basta con definir su comportamiento de presentación y accesibilidad.

## Organización de archivos

Los recursos alojados dentro del repositorio se almacenarán bajo `assets/` y conservarán la misma lógica funcional de la documentación:

```text
assets/
└── financiamiento-reembolsable/
    └── promotores/
        └── [codigo-ficha]/
            ├── imagen-principal.webp
            ├── diagrama.svg
            └── ...
```

## Política de almacenamiento

La capa multimedia separa **la ficha** de **la ubicación física del recurso**. Una ficha puede consumir un archivo interno o externo sin cambiar su URL ni su estructura.

### Recursos internos del repositorio

GitHub podrá alojar recursos ligeros y estáticos que formen parte natural de la documentación, por ejemplo:

- imágenes optimizadas;
- diagramas;
- SVG;
- pequeñas animaciones;
- archivos auxiliares ligeros.

Un video pequeño también podrá alojarse directamente cuando sea razonable y se haya optimizado para web.

### Recursos externos

Los recursos pesados o que necesiten streaming, transcodificación, reproducción adaptativa, almacenamiento especializado o distribución mediante CDN deberán alojarse fuera del repositorio.

Esto incluye, como criterio general:

- videos largos o pesados;
- audio de larga duración;
- animaciones de gran tamaño;
- modelos 3D pesados;
- experiencias interactivas complejas;
- archivos descargables de gran tamaño.

El repositorio conservará la referencia estable al recurso, no una copia innecesaria del archivo.

No se fija todavía un umbral rígido en MB. Ese límite podrá definirse posteriormente en función del proveedor de publicación y del rendimiento observado.

### Reproducción de video interno

Cuando un video esté alojado directamente en el repositorio podrá incorporarse a la ficha con HTML compatible con móvil:

```html
<video controls playsinline width="100%">
  <source src="/como-funciona/assets/financiamiento-reembolsable/promotores/[codigo-ficha]/video.mp4" type="video/mp4">
</video>
```

La reproducción debe mantener controles visibles, comportamiento `playsinline` y un fallback accesible.

### Reproducción de video externo

Cuando el video se aloje en un proveedor externo, la ficha deberá utilizar una referencia o integración embebida estable. El proveedor puede cambiar en el futuro sin modificar la URL canónica de la ficha.

La arquitectura no queda vinculada a un proveedor concreto. Podrá utilizar almacenamiento propio, CDN, plataforma de video o cualquier infraestructura posterior que cumpla los requisitos de disponibilidad, rendimiento, privacidad y accesibilidad.

## Modelo de metadatos

Cada ficha podrá declarar cero, uno o varios recursos mediante una colección `media`.

Ejemplo:

```yaml
media:
  - id: fr-pro-03-01-resumen
    type: image
    src: /assets/financiamiento-reembolsable/promotores/fr-pro-03-01/resumen.webp
    storage: internal
    purpose: resumen
    alt: Resumen de colaboradores requeridos según el monto solicitado
    caption: Colaboradores requeridos según el rango de financiamiento.
    placement: after-summary
    version: 1
    source: guia-fr
    status: approved
```

Ejemplo de recurso externo:

```yaml
media:
  - id: fr-pro-03-01-explicacion
    type: video
    src: https://...
    storage: external
    provider: [proveedor]
    purpose: explicacion
    placement: after-summary
    version: 1
    status: approved
```

## Campos comunes

| Campo | Función |
|---|---|
| `id` | Identificador único y estable del recurso dentro de la documentación. |
| `type` | Tipo de recurso. Es extensible. |
| `src` | Ruta interna o URL externa estable. |
| `storage` | Indica si el recurso es `internal` o `external`. |
| `provider` | Proveedor externo, cuando corresponda. |
| `purpose` | Función didáctica: resumen, explicación, ejemplo, demostración, apoyo, descarga u otra. |
| `alt` | Texto alternativo cuando sea aplicable. |
| `caption` | Texto visible opcional asociado al recurso. |
| `placement` | Ubicación lógica dentro de la ficha. |
| `version` | Versión del recurso. |
| `source` | Fuente funcional o editorial que respalda su contenido. |
| `status` | Estado editorial del recurso. |

Cada tipo podrá incorporar propiedades específicas adicionales sin alterar estos campos comunes.

## Ubicaciones lógicas

Como valores iniciales de `placement`:

- `after-summary`: después de la respuesta breve.
- `within-explanation`: dentro de la explicación, junto al concepto que desarrolla.
- `after-steps`: después de una tabla, lista o procedimiento.
- `example`: asociado al ejemplo práctico.
- `before-action`: antes de «Qué debes hacer».
- `supplementary`: material complementario al final de la ficha.

La ubicación debe responder a una función didáctica, no a una regla estética rígida.

## Reglas editoriales y técnicas

1. El recurso multimedia no sustituye la explicación textual esencial.
2. No puede introducir reglas que no estén respaldadas por la fuente aprobada.
3. Cada recurso debe ser comprensible y accesible en móvil.
4. Las imágenes informativas deben disponer de texto alternativo adecuado.
5. Los videos deben utilizar controles compatibles con móvil y, cuando corresponda, subtítulos o transcripción.
6. Los archivos deben optimizarse para evitar cargas innecesarias.
7. GitHub no debe convertirse en un almacén masivo de video ni de otros archivos pesados.
8. La ubicación física de un recurso puede cambiar sin alterar la URL estable de la ficha.
9. La actualización de un recurso no debe modificar la URL estable de la ficha.
10. Una ficha puede existir sin multimedia; la capa multimedia es complementaria.
11. Cuando se introduzca un nuevo formato, debe definirse su comportamiento de accesibilidad, presentación y fallback antes de usarlo de forma general.

## Fallback

Toda ficha debe seguir siendo útil si el recurso multimedia no carga o no puede reproducirse. El contenido esencial permanecerá disponible mediante texto y, cuando sea necesario, mediante una descripción alternativa.

## Implantación

La incorporación será progresiva:

1. definir el recurso;
2. decidir si su almacenamiento será interno o externo;
3. asociarlo a una ficha concreta;
4. validar contenido y fuente;
5. comprobar visualización móvil;
6. validar accesibilidad;
7. publicar;
8. reutilizar el patrón en otras fichas cuando haya sido aprobado.

La primera implementación servirá como ficha piloto antes de extender la capa multimedia de forma masiva.
