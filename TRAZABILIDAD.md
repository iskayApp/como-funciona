# Trazabilidad de contenido derivado · Cómo funciona

Este documento define cómo detectar cuándo un recurso multimedia o pieza distribuida puede haber quedado desactualizada respecto de su ficha canónica.

## Principio

Cada ficha canónica mantiene un número entero `content_version`.

Cada recurso derivado registra `derived_from_version`, que indica la versión de la ficha con la que fue producido o revisado.

Cuando:

```text
derived_from_version != content_version
```

el recurso debe considerarse **potencialmente desactualizado** y pasar a revisión.

Esto no significa necesariamente que el recurso sea incorrecto; significa que la ficha cambió después de producirlo y debe comprobarse si el cambio afecta al recurso.

## Ejemplo

Ficha canónica:

```yaml
code: "FR-PRO-09"
content_version: 3
reviewed: "2026-11-01"
```

Video asociado:

```yaml
distribution:
  youtube:
    - id: "fr-pro-09-video-pagos"
      video_id: "XXXXXXXXXXX"
      derived_from_version: 2
      status: approved
      reviewed: "2026-10-20"
```

Resultado:

```text
Ficha: versión 3
Video: derivado de versión 2
→ REVISAR
```

## Estados recomendados

Los recursos derivados podrán utilizar:

- `draft`
- `review`
- `approved`
- `stale`
- `archived`

`stale` significa que existe una diferencia de versión o una modificación de fuente que requiere revisión.

## Campos mínimos de un recurso derivado

Todo recurso distribuido debe conservar:

- `id`
- `type` o `platform`
- `source`
- `version`
- `derived_from_version`
- `status`
- `reviewed`

Cuando corresponda también:

- `provider`
- `video_id`
- `asset_id`
- `visibility`
- `url`

## Regla de actualización

Cuando una modificación funcional cambie el contenido de una ficha:

1. aumentar `content_version`;
2. conservar la URL canónica;
3. identificar recursos con una versión derivada anterior;
4. marcarlos para revisión;
5. actualizar únicamente los recursos realmente afectados;
6. registrar su nueva `derived_from_version` y fecha `reviewed`.

Los cambios puramente visuales o técnicos que no alteren la información funcional no requieren necesariamente incrementar `content_version`.

## Objetivo de automatización

El repositorio deberá poder generar en el futuro un reporte como:

```text
FR-PRO-09 cambió de versión 2 a 3.

Revisión requerida:
- YouTube: fr-pro-09-video-pagos
- Facebook: fr-pro-09-fb-01
- Instagram: fr-pro-09-ig-01
- TikTok: fr-pro-09-tt-01

Actualizados:
- Animación interna fr-pro-09-flujo-pagos
```

La comparación debe basarse en metadatos estructurados y no en búsquedas manuales.

## Relación con la fuente

La guía aprobada sigue siendo la fuente funcional. La cadena de dependencia es:

```text
Fuente aprobada
→ ficha canónica + content_version
→ recurso derivado + derived_from_version
→ canal de distribución
```

Esta estructura permite crecer hacia validaciones automáticas mediante GitHub Actions sin cambiar el modelo de datos.
