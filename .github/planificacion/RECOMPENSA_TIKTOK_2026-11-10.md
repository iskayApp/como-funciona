# Recompensa · Vinculación de publicaciones oficiales TikTok

Fecha: 10 de noviembre de 2026 · Catálogo común de «Cómo funciona».
Estado: **asociación multimedia de prueba; revisión editorial pendiente**.

## Fuente comprobada
- Inventario: TikTok Display API `video.list` de la cuenta conectada `@iskay.app`, contenido generado para mantenimiento en la ejecución de GitHub Pages [42904735807](https://github.com/iskayApp/como-funciona/actions/runs/42904735807), `mantenimiento/status.json`.
- `generated_at`: `2026-11-10T21:35:33.164086+00:00`.
- Inventario completo informado por la conexión: **16 publicaciones públicas**, 9 ya vinculadas a FR/Donación, 7 pendientes.
- **Recompensa: 2 publicaciones, ambas de Promotores**. Ninguna verificada con enfoque específico de Contribuyentes o Colaboradores.
- Registros canónicos: `_data/recompensa_tiktok_publicaciones.json`. No se infieren URLs, IDs ni categorías por coincidencias numéricas.

## Matriz de vinculación, con límites de alcance

| Código publicitario | Vídeo TikTok | Público | Ficha canónica | Relación | Qué justifica el enlace | Qué NO explica |
| --- | --- | --- | --- | --- | --- | --- |
| PRO-ENT-01 | [¿Qué te detiene?](https://www.tiktok.com/@iskay.app/video/7678066820368059670) · 2026-08-25 | Promotores | CF-REC-PRO-001 | Complementaria | Reconocer frenos iniciales: recursos, estructura, equipo | No es una explicación de quién puede ser promotor ni de requisitos legales |
| PRO-ENT-02 | [Si solo pudieras resolver una cosa…](https://www.tiktok.com/@iskay.app/video/7678427855948221718) · 2026-08-26 | Promotores | CF-REC-PRO-004 | Complementaria | Priorizar recursos, estructura, equipo o recompensa antes de preparar la información inicial | No enumera campos de «Datos generales» ni sustituye instrucciones |

Producción contrastada:
- [PRO-ENT-01 · Producción Recompensa](https://docs.google.com/document/d/1il15XjAlBpEM2Z28E32mQKVtRZhr8iMWvNh-jSXEyd4/edit).
- [PRO-ENT-02 · Producción Recompensa](https://docs.google.com/document/d/1PaN9tuwJrmS06aJ61ZdQyGXvuk4tKv9PDsnTVzgmFyw/edit).

## Los tres públicos se mantienen separados

| Público | Vídeos públicos verificados destinados a este público | Asociación canónica |
| --- | ---: | --- |
| Promotores | 2 | CF-REC-PRO-001 y CF-REC-PRO-004, ambas complementarias |
| Contribuyentes | 0 | Ninguna; no atribuir los vídeos de Promotores |
| Colaboradores | 0 | Ninguna; no confundir que un vídeo mencione «equipo» con estar dirigido a trabajadores/colaboradores |

## Implementación transversal
- En los dos conceptos asociados, `_includes/ficha-videos.html` incorpora reproductor con consentimiento de reproducción y enlace a TikTok. No se activa autoplay sin interacción.
- `_includes/share-links.html` genera los tres enlaces: ficha, multimedia con ancla, publicación original.
- `_includes/home-video-gallery.html` suma Recompensa y permite filtrar categoría, rol y etapa.
- Las tres portadas de rol incorporan una sección explícita con los vídeos propios o el aviso de ausencia de publicaciones verificadas.
- `scripts/video_publications.py`, `build_share_catalog.py` y `maintenance_check.py` validan categoría, rol, IDs, URLs y evidencia. Una pieza `PRO-` de Recompensa no puede enlazarse a fichas `CON-` o `COL-`.
- `editorial_status=pending_review` y `reviewed=false` **no se modifican**. Los recursos multimedia no se declaran aprobados por la aprobación de la pieza publicitaria.
- Los vídeos no se reutilizan como guías técnicas; son introductores complementarios. No se modifican `1 Recompensa.docx`, tarifas, textos canónicos ni categorías vecinas.

## Pruebas para cierre
- Tests Python de inventario, separación de públicos y bloqueo de URLs falsas.
- Integración con catálogo y mantenimiento comunes, con revisión pendiente.
- Jekyll: rutas canónicas y anclas existentes, buscador y galería.
- Navegación móvil/escritorio, reproducción con y sin JS; filtro `Recompensa`/ `Promotores` con dos vídeos.
- Despliegue a Pages solo tras integración validada, y confirmación de ejecución de publicación correcta.

**Pendientes de material:** Contribuyentes y Colaboradores solo podrán recibir vídeos al identificarse publicaciones específicas verificadas. Esta ausencia no bloquea sus 14 y 9 fichas textuales, respectivamente.
