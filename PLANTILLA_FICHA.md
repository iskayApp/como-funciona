# Plantilla de ficha de Cómo funciona

Patrón editorial aprobado para redactar las fichas. Los campos entre corchetes son marcadores de trabajo; deben resolverse antes de publicar. Los datos internos se conservarán como metadatos y no forman parte del texto principal dirigido al usuario.

## 1. Título

[Pregunta concreta o acción que el usuario quiere realizar.]

## 2. Respuesta breve

[Una o dos frases que resuelven lo esencial.]

### Recurso multimedia opcional

[Puede incorporarse uno o varios recursos cuando ayuden a comprender mejor la respuesta. El formato no está limitado a imagen o video. Consultar `MULTIMEDIA.md`. Cada multimedia aprobada debe conservar un `id` permanente y una ancla HTML `id="media-<id>"` en el bloque que la representa para permitir el acceso directo automático. Consultar `ENLACES_COMPARTIBLES.md`.]

## 3. Explicación

[Desarrollo breve, claro y didáctico, fiel a la guía aprobada y sin repeticiones innecesarias.]

## 4. Tabla, lista o pasos

[Incluir únicamente cuando facilite comparar opciones, requisitos o procedimientos.]

## 5. Ejemplo práctico

[Opcional. Aplicar la regla sin introducir requisitos nuevos.]

## 6. Qué debes hacer

[Acción concreta que el promotor debe ejecutar después de entender el tema.]

## 7. Importante

[Opcional. Reservado para advertencias realmente necesarias.]

## 8. Siguiente paso

[Enlace a la ficha que continúa el recorrido lógico. Si todavía no existe, registrar el destino como pendiente y no publicar un enlace roto.]

## 9. Datos internos

| Campo | Valor |
|---|---|
| Categoría | [Categoría] |
| Rol | [Rol] |
| Etapa | [Etapa del recorrido] |
| Código | [Pendiente de asignación] |
| Versión canónica | [content_version: 1] |
| Fuente | [Documento y apartado de respaldo] |
| Versión de guía | [Versión identificada; no deducirla del nombre del archivo] |
| Estado | Borrador para revisión |
| Fecha de revisión | [AAAA-MM-DD] |
| URL estable | [Pendiente de definición antes de publicar] |
| Multimedia | [Sin recursos / IDs de recursos asociados] |
| Distribución | [Sin activos / YouTube / Facebook / Instagram / TikTok / otros] |
| Piezas publicitarias vinculadas | [Códigos oficiales confirmados, título, categoría y asset_ids, si se han comprobado] |

## Criterio de revisión

No completar vacíos funcionales con supuestos. Registrar las dudas o discrepancias para resolverlas en la fuente antes de publicar la ficha.

La capa multimedia es complementaria. La ficha debe seguir siendo comprensible si un recurso no carga o no puede reproducirse.


## Metadatos de trazabilidad

Toda ficha publicada debe mantener un campo `content_version`. Los recursos multimedia y activos distribuidos asociados deben registrar `derived_from_version`, además de `source`, `version`, `status` y `reviewed`.

Si `derived_from_version` no coincide con `content_version`, el recurso debe considerarse pendiente de revisión. Consultar `TRAZABILIDAD.md`.

## Correspondencia con producción publicitaria

Una ficha puede relacionarse con varias piezas publicitarias, y una pieza con varias fichas. Declarar `marketing_pieces` solamente cuando el calendario o documento de producción permita verificar el código oficial y la relación conceptual. Usar `asset_ids` para señalar publicaciones/referencias reales de esa pieza ya registradas en `media` o `distribution`. No derivar códigos publicitarios de `FR-PRO-*` ni del identificador técnico del recurso. Ver [ENLACES_COMPARTIBLES.md](./ENLACES_COMPARTIBLES.md).
