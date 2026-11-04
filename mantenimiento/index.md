---
layout: default
title: "Centro de mantenimiento"
description: "Organización por categoría, rol y sección; consulta de fichas, piezas y estado técnico de Cómo funciona."
permalink: /mantenimiento/
eyebrow: "Mantenimiento · Cómo funciona"
---

# Centro de mantenimiento

Explora el contenido por categoría, rol y sección, o busca una ficha y sus piezas vinculadas. Los estados editoriales y el diagnóstico técnico se muestran por separado.

<p class="maint-meta">Panel de consulta de la publicación de prueba. No incorpora funciones de edición ni aprobación. La revisión editorial se realizará posteriormente.</p>

{% include maintenance-hierarchy.html %}

<section id="maintenance-search" class="maint-search" data-catalog-url="{{ '/mantenimiento/share_catalog.json' | relative_url }}" aria-labelledby="maint-search-title">
  <h2 id="maint-search-title">Buscar conceptos y piezas para compartir</h2>
  <p class="maint-meta">Consulta por concepto, código de ficha o código oficial de pieza publicitaria. Los resultados distinguen producción y publicaciones; no se asignan correspondencias sin verificar.</p>
  <div class="maint-search-controls">
    <div class="maint-search-field maint-search-wide">
      <label for="maint-search-text">Concepto, título o código</label>
      <input id="maint-search-text" type="search" placeholder="Ej. FR-PRO-01, garantías, pagos" autocomplete="off">
    </div>
    <div class="maint-search-field">
      <label for="maint-search-category">Categoría</label>
      <select id="maint-search-category"><option value="">Todas las categorías</option></select>
    </div>
    <div class="maint-search-field">
      <label for="maint-search-role">Rol</label>
      <select id="maint-search-role"><option value="">Todos los roles</option></select>
    </div>
    <button type="button" id="maint-search-clear" class="maint-search-clear">Limpiar filtros</button>
  </div>
  <p id="maint-search-count" class="maint-meta" role="status" aria-live="polite">Cargando fichas…</p>
  <p id="maint-search-feedback" class="maint-search-feedback" role="status" aria-live="polite"></p>
  <div id="maint-search-results" class="maint-search-results">
    <p class="maint-meta">Cargando el catálogo actual…</p>
  </div>
</section>

<div id="maintenance-dashboard" class="maintenance-dashboard" data-status-url="{{ '/mantenimiento/status.json' | relative_url }}" data-baseurl="{{ site.baseurl | escape }}" aria-live="polite">
  <p>Cargando estado del sistema…</p>
</div>
<noscript><p>La estructura por categoría, rol y sección puede explorarse sin JavaScript. El buscador de piezas y el diagnóstico técnico necesitan JavaScript.</p></noscript>

<script type="application/json" id="maintenance-category-registry">{{ site.data.categories | jsonify }}</script>
<link rel="stylesheet" href="{{ '/assets/css/maintenance.css' | relative_url }}?v=20261104-base">
<script src="{{ '/assets/js/maintenance-status.js' | relative_url }}?v=20261104-base" defer></script>
<script src="{{ '/assets/js/maintenance-search.js' | relative_url }}" defer></script>
