# Precompra · Preparación técnica sin publicación

**Preparación inicial:** 11 de noviembre de 2026. **Revisión funcional:** 14 de noviembre de 2026.

## Alcance y fuente vigente

Los borradores residen en `.github/staging/precompra/ideas/precompra/`, fuera de `ideas/` y de la lectura del catálogo público. Las 66 fichas reflejan el contenido revisado en Drive y mantienen sus rutas, títulos, códigos, navegación y documento individual de origen.

- [Guía vigente de Precompra](https://docs.google.com/document/d/1_wX6OGVxUrs3I9WF-hDgWiB8MWv9Ysfy/edit): ajustes indispensables cerrados el 14 de noviembre de 2026. No declara número de versión; se conserva `guide_version: No indicada expresamente`.
- [66 fichas completas](https://docs.google.com/document/d/16SG6hjAa2TXkppRTC4nFiEJ3WcTKYMtJfr0ZVH1ORBc) e [índice de documentos individuales](https://docs.google.com/document/d/1OsF4P-KNwlsw3v4FlDDs10bSebXoT448OZQz2CQ1IVY).
- [Matriz CLASIFICAR](https://docs.google.com/document/d/1Pd2yV_rvyVJF1PaCr-3zaPm92HS6oKIOXt__I5gFxME): 116 reglas; los 108 IDs originales se conservan y se añaden CL-PRE-109–116.
- [ORGANIZAR](https://docs.google.com/document/d/1FbmMyre6u582qyUihGjMlINoj6vMj2bDtLvQTlrI0qI) e [IDENTIFICAR](https://docs.google.com/document/d/1vYuOqJx-jnm0ltWp25XdIA6YL4I-D2HS0ez0airYjyI): 19 etapas y 66 fichas, con 36 de Promotores, 21 de Precompradores y 9 de Colaboradores.
- 42 fichas tienen cambios funcionales y `content_version: 2`; 24 conservan `content_version: 1`.
- `functional_review_status: completed` y `functional_reviewed_on: 2026-11-14` documentan el contraste con la guía. La revisión editorial del propietario continúa pendiente.

La matriz local `clasificacion.json` conserva el texto, tipo, actor y apartado fuente de cada regla. Las referencias de las fichas cubren las 116 reglas. Las descripciones de los borradores coinciden con su respuesta breve.

## Cambios funcionales trasladados

La revisión recoge la opcionalidad de colaboradores y los cuatro perfiles coincidentes en descuentos y formulario. Conserva otros roles como funciones adicionales acordables. Las campañas de USD 10.000,00 a USD 470.000,00 permiten elegir seguro de cumplimiento o prenda, con presentación dentro de los 15 días hábiles posteriores al cierre y validación antes de transferir fondos. La carta con el representante acompaña a la prenda. La póliza identifica a los precompradores protegidos, el importe y el procedimiento de reclamación; la aseguradora debe estar autorizada para operar en Ecuador.

Las reclamaciones se registran y derivan al canal correspondiente; iskay.app no asume representación jurídica, ejecución de garantías o seguimiento jurídico. Las garantías no aseguran por sí solas entrega o recuperación íntegra. La falta de documentación se considera en cualquiera de las etapas, conservando la distinción entre revisión y reversión procedente.

## Observaciones y comprobación operativa

OBS-PRE-01, 02, 03 y 08 reflejan aclaraciones resueltas en la fuente vigente. OBS-PRE-04 a 07 conservan los criterios aplicados sobre modalidad flexible, reversión, notificaciones y tarifas. No quedan ajustes indispensables de la guía abiertos por esas observaciones. Su trazabilidad por ficha se mantiene en `observaciones.json`.

Las nueve comprobaciones de `funciones_pendientes.json` mantienen `evidence: no_verificada`. El contraste documental no acredita implementación operativa. Los tres candidatos de marketing permanecen sin vincular, con cero URLs públicas verificadas; se conserva como histórica la información de sus calendarios.

## Bloqueos de publicación

1. `_config.yml` mantiene `ideas/precompra` en `exclude`.
2. `_data/categories.yml` conserva `status: preparation` y `roles: []`.
3. Fichas e índices mantienen `status: draft`, `publication_status: not_published`, `published: false`, `visibility: private`, `editorial_status: pending_review` y `reviewed: false`.
4. GitHub Pages se despliega únicamente desde `main`; esta rama de preparación no activa despliegue.
5. La revisión funcional de las fichas no constituye autorización editorial ni de publicación.
6. El repositorio es público: los borradores pueden verse como código en GitHub, aunque no aparecen en el sitio publicado.

## Antes de publicar

- Completar la revisión editorial del propietario y obtener la autorización de publicación correspondiente.
- Comprobar las funcionalidades y condiciones operativas pendientes.
- Vincular medios y piezas de marketing después de verificar sus relaciones y URLs originales.
- Autorizar los cambios de `exclude`, catálogo, roles y banderas de publicación.
- Ejecutar las validaciones de enlaces, catálogo, navegación, móvil y mantenimiento de la etapa de publicación.

## Validación de esta sincronización

Las pruebas de Precompra comprueban el inventario, la matriz de 116 reglas, su cobertura, el reparto de versiones de esta revisión, la separación entre revisión funcional y editorial, la trazabilidad de observaciones y las salvaguardas de publicación. El contraste con las fichas individuales de Drive comprueba las cinco secciones, las referencias, la fuente y los metadatos revisados sin alterar la navegación.
