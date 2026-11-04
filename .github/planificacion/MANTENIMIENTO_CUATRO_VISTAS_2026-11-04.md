# Mantenimiento · cuatro vistas

## Alcance

Continuación del punto 3 aprobado: completar el centro de mantenimiento antes de propagar Donación. Se conserva íntegramente `ideas/`, sus 99 fichas FR, textos, códigos, URL, versiones y estados editoriales. No se realiza revisión editorial ni se altera Drive. No cambia la portada pública ni sus buscadores/orientación.

## Vistas

1. Contenido y estructura: jerarquía nativa, filtros de título/código/fuente, categoría, rol y sección; control por ficha con fuente literal, secciones, versión, fecha registrada y tres estados independientes.
2. Multimedia y marketing: mantiene el componente existente y sus tres enlaces cuando existen; acceso directo desde el control de ficha; los recursos no vinculados del reporte técnico se muestran en esta vista. No se infieren asociaciones ni se incrustan recursos automáticamente.
3. Revisiones y cambios: colas de aprobación pendiente, ausencia de estado explícito, datos incompletos, diferencias de versiones y recursos derivados de otra versión. Consulta de impacto por referencias literales de guía/sección. Enlace al control editorial original #9 sin cerrar hallazgos ni sincronizar su estado.
4. Estado técnico y publicación: versión y referencia de la compilación, publicación de prueba, aprobación explícita o no registrada y resultado técnico separado. Sin reporte, el estado es «Sin comprobar».

## Datos y seguridad

`scripts/build_maintenance_control.py` produce una vista de lectura de metadatos públicos; no es otra fuente editable de contenido. Las fichas son fuente de versiones y aprobaciones; `share_catalog.json` sigue siendo fuente de asociaciones multimedia/marketing. El generador aplica lista explícita de campos, excluye privados, borradores y rutas excluidas y no exporta cuerpos, notas libres ni documentos privados. Los valores variables se pintan como texto del DOM, no como HTML.

`_data/maintenance-public.yml` admite únicamente referencias expresamente publicables de trabajo y cambios. Actualmente no se han cargado versiones de trabajo ni eventos de cambios de guía; el panel lo indica sin asumir que Drive esté sincronizado. Un mismo número de versión NO demuestra identidad de contenido; solo se contrasta una huella cuando existe evidencia registrada. El documento editorial privado no se enlaza desde esta proyección.

IMPORTANTE: el repositorio y el panel son públicos. No guardar información privada ni siquiera en campos omitidos por el generador. Un administrador autenticado, edición, aprobaciones y sincronización con Drive requieren una fase independiente y una ubicación protegida. No se han implementado ni simulado esas funciones.

## Verificación

Se mantienen todas las pruebas de FR y de la base general. Se añaden pruebas de proyección mínima, ausencia de datos privados, preservación de aprobaciones, separación de estados, comparación de versiones, filtros y aislamiento de fuentes. El sitio generado se recorre desde la portada para bloquear rutas canónicas ausentes, duplicadas o inaccesibles antes de publicar.

Las pruebas de navegador cubren 1280, 390 y 320 px, teclado, cuatro vistas, filtros, control por ficha, enlace al buscador de marketing, colas e impacto, navegación sin JavaScript y fallos de catálogos. El reporte de servicios usado en esas pruebas es sintético y no certifica TikTok. Capturas y resultados quedan en los artefactos del flujo de validación.

## Orden

No se inicia todavía Donación. Después de completar la base y el mantenimiento, su incorporación seguirá CLASIFICAR → ORGANIZAR → IDENTIFICAR → DESARROLLAR desde su propia guía.
