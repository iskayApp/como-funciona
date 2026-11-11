# Precompra · Preparación técnica sin publicación · 11/11/2026

## Alcance

Los borradores residen en `.github/staging/precompra/ideas/precompra/`, fuera de `ideas/` y de la lectura del catálogo público. Sus rutas de destino y metadatos quedan preparados para una futura publicación autorizada.

- Fuente editorial: [66 fichas completas](https://docs.google.com/document/d/16SG6hjAa2TXkppRTC4nFiEJ3WcTKYMtJfr0ZVH1ORBc/edit).
- Índice de documentos individuales: [00 CF-PRE](https://docs.google.com/document/d/1OsF4P-KNwlsw3v4FlDDs10bSebXoT448OZQz2CQ1IVY/edit).
- Guía original: «1 Precompra.docx» (sin modificaciones).
- 108 registros de CLASIFICAR; 19 etapas; 66 fichas: 36 Promotores, 21 Precompradores, 9 Colaboradores.
- En cada ficha: respuesta breve, explicación, acción, advertencia, siguiente paso, fuente, referencias y estado editorial.
- Ninguna pieza publicitaria o URL multimedia se vincula sin comprobación específica.

## Bloqueos de publicación (NO quitar durante la preparación)

1. `_config.yml` mantiene `ideas/precompra` en `exclude`.
2. `_data/categories.yml` conserva `status: preparation` y `roles: []`.
3. Todos los archivos de fichas y recorridos mantienen `status: draft`, `publication_status: not_published`, `published: false`, `visibility: private`, `editorial_status: pending_review` y `reviewed: false`.
4. GitHub Pages se despliega únicamente desde `main`; esta rama no activa despliegue.
5. Esta rama prepara la integración, no supone autorización editorial ni publicación de fichas.
6. GitHub es un repositorio **público**: el código de esta rama puede verse en GitHub, aunque no se muestra en el sitio publicado.

## Observaciones abiertas en origen

- OBS-PRE-01: carácter opcional de colaboradores.
- OBS-PRE-02: perfiles de colaboradores no coincidentes.
- OBS-PRE-03: relación entre seguro, prenda y carta de compromiso.
- OBS-PRE-04: límites de la modalidad flexible.
- OBS-PRE-05: revisión de causales y reversión.
- OBS-PRE-06: notificaciones frente a confirmación bancaria.
- OBS-PRE-07: siete tramos, comisión mínima y límite documentado.
- OBS-PRE-08: reclamaciones y alcance de resultados posibles.

## Antes de publicar

- Revisión editorial del propietario o autorización específica para publicación con revisión pendiente.
- Resolver o documentar expresamente las ocho observaciones; validar funcionalidades y condiciones operativas.
- Vincular medios y piezas de marketing únicamente tras verificar sus relaciones y URL originales.
- Autorizar cambios explícitos de `exclude`, catálogo, roles y banderas de publicación.
- Ejecutar pruebas de enlaces, catálogos, navegación por rol, móvil y mantenimiento.
