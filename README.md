# Cómo funciona · iskay.app

Documentación pública de iskay.app para explicar sus categorías, recorridos y procedimientos de forma clara, accesible desde móvil y mantenible mediante control de versiones.

## Principio de arquitectura

La categoría es la unidad funcional principal. La navegación se organiza por categoría, rol, etapa y ficha.

Las cinco categorías de Ideas son Donación, Recompensa, Precompra, Inversión en Acciones y Financiamiento Reembolsable.

## Alcance actual

- El recorrido **Financiamiento Reembolsable · Promotores** está desarrollado por completo.
- El recorrido contiene **33 fichas organizadas en 6 etapas**.
- Cada ficha dispone de una URL pública estable y navegación anterior/siguiente.
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

En cada despliegue se genera `mantenimiento/share_catalog.json`, con fichas y recursos ordenados por categoría, rol, etapa y código, para facilitar la distribución editorial. **El Centro de mantenimiento** (`/mantenimiento/`) incluye una consulta de concepto/título/código, categoría y rol, que muestra las piezas publicables asociadas y permite copiar los tres enlaces disponibles sin trabajar con JSON. Las piezas de distribución que no están insertadas en la ficha no reciben anclas ficticias. Las piezas publicitarias con código oficial se vinculan mediante metadatos `marketing_pieces` y `asset_ids` comprobados; los activos sin vínculo siguen consultables como «sin pieza publicitaria identificada», sin inferir relaciones por coincidencia numérica. Ver [ENLACES_COMPARTIBLES.md](./ENLACES_COMPARTIBLES.md).


## Publicación

El sitio se publica mediante GitHub Pages:

https://iskayapp.github.io/como-funciona/

Las fichas permiten acceso directo sin iniciar sesión ni descargar archivos y están preparadas para lectura desde móvil.

Durante esta fase de prueba pública, el sitio mantiene `noindex: true` para evitar indexación en buscadores hasta que se apruebe su integración definitiva.

## Estado

- Repositorio: **público**.
- Rama principal: `main`.
- GitHub Pages: **activo**.
- Financiamiento Reembolsable · Promotores: **33/33 fichas desarrolladas · PRUEBA PÚBLICA**.
- Etapas 01 a 06: **completas**.
