# CF-UX-001 · Implementación visual

4 de noviembre de 2026. Diseño aprobado mediante las maquetas de portada, recorrido y ficha. Los recursos gráficos provisionales fueron autorizados por el usuario para su uso en el sitio y posterior sustitución.

## Qué cambia

- Portada con bienvenida fotográfica, búsqueda y orientación juntas, elección de recorrido, modalidades, recursos y fichas clave.
- Recursos y títulos resueltos desde las páginas canónicas; no se mantiene un segundo inventario de fichas.
- Modalidades en preparación identificadas sin enlaces a recorridos vacíos.
- Búsqueda con filtros combinables de categoría, rol, etapa y tipo de recurso. Cambiar el contexto descarta selecciones incompatibles. Los resultados siguen siendo fichas canónicas.
- Rol de las fichas antiguas sin `role` resuelto mediante `_data/categories.yml`; se evita duplicar «promotores» y «Promotores».
- Recorridos con índice lateral, adaptable a móvil, y navegación a sus secciones reales.
- Fichas con respuesta breve destacada, índice de encabezados, tabla contenida y enlaces para compartir con títulos comprensibles.
- Tipografía, iconos, componentes y estados de foco comunes. Movimiento reducido y navegación estática conservados.

Los archivos de `ideas/`, los importes, textos, códigos, URLs, estados editoriales y diagramas canónicos no cambian. La nueva presentación no concede aprobación editorial.

## Recursos provisionales y sustitución

La fotografía y las dos miniaturas se generaron para esta implementación. Son recursos decorativos: las miniaturas llevan a los diagramas originales, no los sustituyen ni aportan reglas funcionales.

| Recurso | Archivo / configuración | Cómo reemplazarlo |
| --- | --- | --- |
| Fotografía de bienvenida | `assets/visual/colaboracion-andina.webp`, referencia `hero` en `_data/visual.yml` | Sustituir el archivo o su ruta. Mantener encuadre horizontal con espacio claro para texto a la izquierda y sujetos a la derecha. |
| Símbolo de marca provisional | `assets/visual/simbolo-provisional.svg`, referencia `brand_symbol` | Sustituir por el símbolo oficial con dimensiones equivalentes; revisar el conjunto con la marca textual en `_layouts/default.html`. |
| Miniatura de colaboradores | `assets/visual/colaboradores-preview.webp` | Cambiar la referencia de `fr-pro-13-colaboradores-monto` en `visual.previews`. |
| Miniatura de pagos | `assets/visual/pagos-preview.webp` | Cambiar la referencia de `fr-pro-09-flujo-pagos` en `visual.previews`. |
| Iconos de interfaz | `_includes/ui-icon.html` | Reemplazar las formas manteniendo los nombres de cada icono y sus atributos accesibles. |
| Fichas destacadas | `featured_codes` en `_data/visual.yml` | Modificar únicamente los códigos seleccionados; título, descripción y URL se resuelven desde las fichas. |

Los tres WebP suman aproximadamente 163 KiB. Se conservan los originales de generación fuera del checkout; el sitio utiliza versiones optimizadas. La bienvenida tiene prioridad de carga y las miniaturas usan carga diferida con espacio reservado.

Para una miniatura nueva, asociar la ruta a un ID multimedia existente y mantener accesible el recurso original. Si no hay miniatura configurada, la tarjeta usa la imagen canónica. No modificar identificadores ya publicados para cambiar una imagen.

## Arquitectura de presentación

- `assets/css/knowledge.css`: estilos, medidas, variantes por superficie y adaptación móvil.
- `assets/js/knowledge.js`: índice generado desde los encabezados existentes, respuesta breve, tabla y navegación de secciones. No realiza peticiones ni guarda datos.
- `_includes/home-routes.html`, `home-content.html`, `topic-context.html`: composición a partir de las fuentes existentes.
- La generación del catálogo conserva sus enlaces y añade resolución del rol antiguo desde el registro de navegación.
- Las pruebas anteriores que fijaban el orden de la portada se actualizan al orden aprobado: búsqueda → orientación → categorías. La protección de contenido canónico y de los scripts de orientación y mantenimiento permanece.

## Validación

Desde la raíz del repositorio, usando las herramientas del entorno:

```bash
python scripts/build_share_catalog.py
python scripts/build_maintenance_control.py
jekyll build --destination /ruta/al/sitio
python -m unittest discover -s tests -v
node --test tests/*.test.cjs
python scripts/check_fr_navigation.py /ruta/al/sitio
python scripts/verify_maintenance_site.py /ruta/al/sitio
python scripts/smoke_fr_navigation.py /ruta/al/sitio
python scripts/smoke_fr_explorer.py /ruta/al/sitio
python scripts/smoke_category_base.py /ruta/al/sitio
python scripts/smoke_maintenance_workspace.py /ruta/al/sitio
python scripts/smoke_visual_refresh.py /ruta/al/sitio
```

El entorno de esta tarea activa Ruby/Python mediante `source /workspace/.setup/activate`; Jekyll se invoca con `ruby3.3 /workspace/.setup/ruby/usr/bin/jekyll`. Para usar Chromium instalado en el sistema, exportar `CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium`; sin esa variable se utiliza el navegador de Playwright, como en CI.

`smoke_visual_refresh.py` comprueba cuatro anchos (1280, 768, 390 y 320), filtros y reinicios dependientes, recursos, índice del recorrido, tabla canónica completa, portapapeles, fallo del catálogo y lectura sin JavaScript. Guarda capturas reales en `ui-artifacts/design-*.png`. Estas comprobaciones no son una auditoría completa de accesibilidad ni certifican servicios externos.

La publicación sigue el flujo existente de GitHub Pages al integrar cambios en `main`. La preparación y validación local no publican el sitio.

Validación realizada en esta tarea: compilación Jekyll, 29 pruebas Python, 12 pruebas JavaScript, auditorías de las 99 fichas y los cinco scripts de navegador satisfactorios. Se comprobó además que `ideas/`, las categorías, la configuración de publicación y los SVG canónicos no tienen diferencias respecto a la base.
