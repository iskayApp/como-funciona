# Precompra · Publicación autorizada y revisión editorial posterior

**Preparación inicial:** 11 de noviembre de 2026. **Revisión funcional y autorización de publicación:** 14 de noviembre de 2026.

## Autorización y alcance

Después de la revisión completa en Drive y su sincronización con GitHub, el propietario autoriza publicar Precompra en Cómo funciona y realizar posteriormente la aprobación editorial.

Las 66 fichas pasan de la preparación técnica a `ideas/precompra/`. La categoría incorpora tres recorridos: Promotores (36 fichas, nueve etapas), Precompradores (21 fichas, seis etapas) y Colaboradores (9 fichas, cuatro etapas). Se conservan títulos, códigos, URLs, navegación, contenido revisado y fuentes individuales de Drive.

- [Precompra en Cómo funciona](https://iskayapp.github.io/como-funciona/precompra/)
- [PR #20: integración y validaciones](https://github.com/iskayApp/como-funciona/pull/20)
- [Workflow de publicación](https://github.com/iskayApp/como-funciona/actions/workflows/pages.yml)

La autorización permite integrar y desplegar esta categoría. El resultado efectivo del despliegue se comprueba en GitHub Actions y en las URLs públicas.

## Fuente vigente y trazabilidad

- [Guía vigente de Precompra](https://docs.google.com/document/d/1_wX6OGVxUrs3I9WF-hDgWiB8MWv9Ysfy/edit): ajustes indispensables cerrados el 14 de noviembre de 2026. No declara número de versión; se conserva `guide_version: No indicada expresamente`.
- [66 fichas completas](https://docs.google.com/document/d/16SG6hjAa2TXkppRTC4nFiEJ3WcTKYMtJfr0ZVH1ORBc) e [índice de documentos individuales](https://docs.google.com/document/d/1OsF4P-KNwlsw3v4FlDDs10bSebXoT448OZQz2CQ1IVY).
- [Matriz CLASIFICAR](https://docs.google.com/document/d/1Pd2yV_rvyVJF1PaCr-3zaPm92HS6oKIOXt__I5gFxME): 116 reglas; se conservan los 108 IDs originales y se añaden CL-PRE-109–116.
- [ORGANIZAR](https://docs.google.com/document/d/1FbmMyre6u582qyUihGjMlINoj6vMj2bDtLvQTlrI0qI) e [IDENTIFICAR](https://docs.google.com/document/d/1vYuOqJx-jnm0ltWp25XdIA6YL4I-D2HS0ez0airYjyI): 19 etapas y 66 fichas.
- La revisión corrigió el contenido de 42 fichas (`content_version: 2`); 24 conservaron su contenido (`content_version: 1`). La publicación no incrementa esas versiones.
- `functional_review_status: completed` y `functional_reviewed_on: 2026-11-14` documentan el contraste con la guía.

Los controles de clasificación, observaciones, funciones y candidatos audiovisuales conservan su ubicación en `.github/staging/precompra/` para mantener sus referencias. Las fichas canónicas publicables residen únicamente en `ideas/precompra/`.

## Revisión editorial posterior

La publicación técnica y la aprobación editorial son estados distintos:

| Campo | Estado de las fichas |
|---|---|
| `status` | `published` |
| `published` | `true` |
| `visibility` | `public` |
| `publication_status` | `published` |
| `editorial_status` | `pending_review` |
| `reviewed` | `false` |

El componente común conserva el aviso de revisión editorial pendiente. El centro de mantenimiento muestra ese estado y enlaza este control. Ninguna ficha se marca como aprobada por el hecho de publicarse.

## Integración en Cómo funciona

- La categoría se registra como disponible y se retira su exclusión de Jekyll.
- Sus tres roles y 19 etapas utilizan los componentes de navegación comunes.
- Las 66 fichas se incorporan al catálogo compartido, buscador, orientación guiada y mantenimiento.
- Los metadatos de la categoría y de cada ficha alimentan esas interfaces; no se crea otro catálogo ni se modifica el buscador.
- Se conserva `noindex: true` del sitio y la separación entre categorías y roles.

## Contenido revisado y controles pendientes

Las fichas recogen la elección entre seguro de cumplimiento y prenda para campañas de USD 10.000,00 a USD 470.000,00, la presentación dentro de los 15 días hábiles posteriores al cierre y la validación antes de transferir fondos. La carta con el representante acompaña a la prenda. La póliza identifica a los precompradores protegidos, el importe y el procedimiento de reclamación.

También reflejan los cuatro perfiles de colaboradores, su incorporación opcional y el registro y derivación de reclamaciones por iskay.app, con los límites establecidos en la guía. Esta publicación conserva íntegramente el contenido ya contrastado en Drive.

OBS-PRE-01, 02, 03 y 08 registran aclaraciones resueltas en la fuente. OBS-PRE-04 a 07 recogen los criterios aplicados sobre modalidad flexible, reversión, notificaciones y tarifas. No quedan ajustes indispensables de la guía abiertos por esas observaciones.

Las nueve comprobaciones de `funciones_pendientes.json` siguen con `evidence: no_verificada`: publicar documentación en Cómo funciona no acredita la implementación operativa en Avatar. Los tres candidatos audiovisuales permanecen sin vincular mientras no existan URLs originales y correspondencias verificadas.

## Validación de publicación

Las pruebas comprueban las 66 fichas, sus versiones y 116 referencias, los 23 índices, la continuidad de navegación y los estados editoriales pendientes. Los controles generales verifican el catálogo de 258 fichas en cuatro categorías y doce roles, el renderizado, los enlaces, el buscador, la orientación, mantenimiento y la navegación de escritorio y móvil.

La comprobación final contrasta el despliegue con la revisión integrada en `main` y abre las rutas públicas de Precompra.
