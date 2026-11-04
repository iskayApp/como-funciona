---
layout: default
title: "Centro de mantenimiento"
description: "Contenido, multimedia, revisiones y publicación de Cómo funciona, organizados por categoría y rol."
permalink: /mantenimiento/
eyebrow: "Mantenimiento · Cómo funciona"
---

# Centro de mantenimiento

Encuentra una ficha, consulta sus recursos y distingue lo publicado de lo que necesita revisión.

<p class="maintenance-boundary">Consulta pública · No modifica contenidos, no aprueba fichas y no publica cambios. Los documentos privados y las notas internas no se incorporan a esta interfaz.</p>

<div id="maintenance-workspace" data-control-url="{{ '/mantenimiento/control_catalog.json' | relative_url }}" data-share-url="{{ '/mantenimiento/share_catalog.json' | relative_url }}">
  <nav class="maintenance-view-nav" aria-label="Vistas de mantenimiento">
    <a href="#m-contenido" data-maint-view-link="m-contenido">Contenido y estructura</a>
    <a href="#m-multimedia" data-maint-view-link="m-multimedia">Multimedia y marketing</a>
    <a href="#m-revisiones" data-maint-view-link="m-revisiones">Revisiones y cambios</a>
    <a href="#m-publicacion" data-maint-view-link="m-publicacion">Estado técnico y publicación</a>
  </nav>
  <p id="workspace-load-status" class="maint-meta" role="status" aria-live="polite">Cargando datos de control…</p>
  <div id="workspace-filters" class="workspace-filters" hidden>
    <div class="maint-search-field workspace-query"><label for="control-query">Buscar una ficha</label><input id="control-query" type="search" placeholder="Título, código o referencia funcional" autocomplete="off"></div>
    <div class="maint-search-field"><label for="control-category">Categoría</label><select id="control-category"><option value="">Todas las categorías</option></select></div>
    <div class="maint-search-field"><label for="control-role">Rol</label><select id="control-role"><option value="">Todos los roles</option></select></div>
    <div class="maint-search-field"><label for="control-section">Sección</label><select id="control-section"><option value="">Todas las secciones</option></select></div>
    <button id="control-clear" type="button" class="workspace-button">Limpiar filtros</button>
    <p id="control-count" class="maint-meta workspace-filter-count" role="status" aria-live="polite"></p>
  </div>

  <section id="m-contenido" class="maintenance-view" data-maint-view aria-labelledby="content-view-title">
    <h2 id="content-view-title">Contenido y estructura</h2>
    <p class="maint-meta">Explora el recorrido o abre el control de una ficha para consultar su fuente, versión y estados.</p>
    <section id="topic-control" class="topic-control" aria-labelledby="topic-control-title" hidden></section>
    {% include maintenance-hierarchy.html %}
    <section class="workspace-preparation" aria-labelledby="preparation-title">
      <h3 id="preparation-title">Contenido en preparación</h3>
      <p class="maint-meta">Clasificar → Organizar → Identificar → Desarrollar. Solo se muestran fases y referencias registradas expresamente, sin inferir el avance a partir de la publicación.</p>
      <div id="preparation-records"><p class="maint-meta">Las categorías sin recorrido continúan en preparación.</p></div>
    </section>
  </section>

  <section id="m-multimedia" class="maintenance-view" data-maint-view aria-labelledby="media-view-title">
    <h2 id="media-view-title">Multimedia y marketing</h2>
    <p class="maint-meta">Ficha canónica → Pieza publicitaria → Recursos y publicaciones. Vincular un recurso no significa insertarlo dentro de la ficha.</p>
    <section id="maintenance-search" class="maint-search" data-catalog-url="{{ '/mantenimiento/share_catalog.json' | relative_url }}" aria-labelledby="maint-search-title">
      <h3 id="maint-search-title">Buscar conceptos y piezas para compartir</h3>
      <p class="maint-meta">Conserva los códigos oficiales. Los recursos sin correspondencia verificada se identifican por separado.</p>
      <div class="maint-search-controls">
        <div class="maint-search-field maint-search-wide"><label for="maint-search-text">Concepto, título o código</label><input id="maint-search-text" type="search" placeholder="Ej. FR-PRO-13, garantías, pagos" autocomplete="off"></div>
        <div class="maint-search-field"><label for="maint-search-category">Categoría</label><select id="maint-search-category"><option value="">Todas las categorías</option></select></div>
        <div class="maint-search-field"><label for="maint-search-role">Rol</label><select id="maint-search-role"><option value="">Todos los roles</option></select></div>
        <button type="button" id="maint-search-clear" class="maint-search-clear">Limpiar filtros</button>
      </div>
      <p id="maint-search-count" class="maint-meta" role="status" aria-live="polite">Cargando fichas…</p>
      <p id="maint-search-feedback" class="maint-search-feedback" role="status" aria-live="polite"></p>
      <div id="maint-search-results" class="maint-search-results"><p class="maint-meta">Cargando el catálogo actual…</p></div>
    </section>
    <div id="marketing-unlinked"><p class="maint-meta">El inventario de recursos pendientes de vinculación se mostrará cuando esté disponible el reporte técnico.</p></div>
  </section>

  <section id="m-revisiones" class="maintenance-view" data-maint-view aria-labelledby="review-view-title">
    <h2 id="review-view-title">Revisiones y cambios</h2>
    <p class="maint-meta">Colas de trabajo para la revisión posterior. Consultarlas no cambia aprobaciones ni cierra hallazgos.</p>
    <div id="editorial-control-links"></div>
    <div class="maint-search-field review-kind-field"><label for="review-kind">Qué necesitas revisar</label><select id="review-kind"><option value="pending">Pendientes de revisión editorial</option><option value="unspecified">Sin estado editorial explícito</option><option value="metadata">Datos de control incompletos</option><option value="versions">Diferencias con referencias en preparación</option><option value="media">Multimedia derivada de otra versión</option></select></div>
    <p id="review-count" class="maint-meta" role="status" aria-live="polite"></p>
    <div id="review-records"></div><button id="review-more" type="button" class="workspace-button" hidden>Mostrar más fichas</button>
    <section class="source-impact" aria-labelledby="impact-title">
      <h3 id="impact-title">¿Qué puede afectar un cambio en la guía?</h3>
      <p class="maint-meta">Selecciona una referencia y su sección para localizar fichas y recursos asociados. Se consultan todas las fichas con esa referencia, al margen de los filtros superiores. No detecta cambios en Drive ni sustituye la revisión funcional.</p>
      <div class="impact-controls"><div class="maint-search-field"><label for="impact-source">Fuente declarada</label><select id="impact-source"><option value="">Elige una fuente</option></select></div><div class="maint-search-field"><label for="impact-section">Sección de la fuente</label><select id="impact-section" disabled><option value="">Todas las referencias de esta fuente</option></select></div></div>
      <p id="impact-count" class="maint-meta" role="status" aria-live="polite"></p><div id="impact-records"></div>
      <h3>Cambios registrados</h3><div id="guide-change-records"><p class="maint-meta">Cargando registros de cambio…</p></div>
    </section>
  </section>

  <section id="m-publicacion" class="maintenance-view" data-maint-view aria-labelledby="publication-view-title">
    <h2 id="publication-view-title">Estado técnico y publicación</h2>
    <p class="maint-meta">Tres controles independientes: aprobación editorial, disponibilidad en esta publicación y resultado de la comprobación técnica.</p>
    <div id="publication-summary" class="workspace-summary"></div>
    <p id="publication-build" class="maint-meta"></p>
    <div id="publication-records"></div><button id="publication-more" type="button" class="workspace-button" hidden>Mostrar más fichas</button>
    <div id="maintenance-dashboard" class="maintenance-dashboard" data-status-url="{{ '/mantenimiento/status.json' | relative_url }}" data-baseurl="{{ site.baseurl | escape }}" aria-live="polite"><p>Cargando estado del sistema…</p></div>
  </section>
</div>

<noscript><p>Sin JavaScript puedes recorrer las cuatro secciones y explorar la jerarquía de fichas. Los filtros, controles por ficha, consultas de multimedia y diagnóstico necesitan JavaScript.</p></noscript>
<script type="application/json" id="maintenance-category-registry">{{ site.data.categories | jsonify }}</script>
<link rel="stylesheet" href="{{ '/assets/css/maintenance.css' | relative_url }}?v=20261104-base">
<link rel="stylesheet" href="{{ '/assets/css/maintenance-workspace.css' | relative_url }}?v=20261104-vistas">
<script src="{{ '/assets/js/maintenance-workspace.js' | relative_url }}?v=20261104-vistas" defer></script>
<script src="{{ '/assets/js/maintenance-status.js' | relative_url }}?v=20261104-base" defer></script>
<script src="{{ '/assets/js/maintenance-search.js' | relative_url }}" defer></script>
