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

Los archivos pesados o que requieran streaming, procesamiento especializado o infraestructura externa podrán alojarse fuera del repositorio. La ficha conservará únicamente su referencia estable.

## Modelo de metadatos

Cada ficha podrá declarar cero, uno o varios recursos mediante una colección `media`.

Ejemplo:

```yaml
media:
  - id: fr-pro-03-01-resumen
    type: image
    src: /assets/financiamiento-reembolsable/promotores/fr-pro-03-01/resumen.webp
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
7. Los recursos pesados pueden alojarse externamente; GitHub no debe convertirse en un repositorio masivo de video.
8. La actualización de un recurso no debe modificar la URL estable de la ficha.
9. Una ficha puede existir sin multimedia; la capa multimedia es complementaria.
10. Cuando se introduzca un nuevo formato, debe definirse su comportamiento de accesibilidad, presentación y fallback antes de usarlo de forma general.

## Fallback

Toda ficha debe seguir siendo útil si el recurso multimedia no carga o no puede reproducirse. El contenido esencial permanecerá disponible mediante texto y, cuando sea necesario, mediante una descripción alternativa.

## Implantación

La incorporación será progresiva:

1. definir el recurso;
2. asociarlo a una ficha concreta;
3. validar contenido y fuente;
4. comprobar visualización móvil;
5. validar accesibilidad;
6. publicar;
7. reutilizar el patrón en otras fichas cuando haya sido aprobado.

La primera implementación servirá como ficha piloto antes de extender la capa multimedia de forma masiva.
