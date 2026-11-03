---
layout: default
title: "Cómo funciona · Financiamiento Reembolsable"
description: "Recorridos de Promotores, Inversores y Colaboradores de Financiamiento Reembolsable en iskay.app."
permalink: /
eyebrow: "Financiamiento Reembolsable · Guía de uso"
---

# Cómo funciona

Explora **Financiamiento Reembolsable** desde tu rol o busca directamente la explicación que necesitas.

{% include fr-context.html %}
{% include fr-role-cards.html %}

<section id="buscar" class="public-search" data-catalog-url="{{ '/mantenimiento/share_catalog.json' | relative_url }}" data-site-root="{{ '/' | absolute_url }}" aria-labelledby="public-search-title">
  <h2 id="public-search-title">¿Qué necesitas saber?</h2>
  <p class="public-search-description">Busca una explicación y encuentra la respuesta que necesitas.</p>

  <form id="public-search-form" class="public-search-form" role="search" aria-label="Buscar en Cómo funciona">
    <label class="public-search-sr-only" for="public-search-query">Buscar una explicación</label>
    <span class="public-search-icon" aria-hidden="true">
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"></circle><path d="m16 16 5 5"></path></svg>
    </span>
    <input id="public-search-query" type="search" placeholder="Buscar temas, preguntas o códigos…" autocomplete="off" enterkeyhint="search" disabled>
    <button id="public-search-submit" class="public-search-submit" type="submit" disabled>Buscar</button>
  </form>

  <div id="public-search-tools" class="public-search-tools" hidden>
    <button id="public-search-filter-toggle" class="public-search-filter-toggle" type="button" aria-expanded="false" aria-controls="public-search-filters" disabled>
      <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M7 12h10M10 17h4"></path></svg>
      Filtrar resultados
    </button>
    <button id="public-search-clear" class="public-search-clear" type="button" disabled>Limpiar búsqueda</button>
  </div>

  <div id="public-search-filters" class="public-search-filters" hidden>
    <div class="public-search-field">
      <label for="public-search-category">Categoría</label>
      <select id="public-search-category" disabled><option value="">Todas las categorías</option></select>
    </div>
    <div class="public-search-field">
      <label for="public-search-role">Dirigido a</label>
      <select id="public-search-role" disabled><option value="">Todos los roles</option></select>
    </div>
  </div>

  <p id="public-search-count" class="public-search-count" role="status" aria-live="polite"></p>
  <div id="public-search-results" class="public-search-results"></div>
  <button id="public-search-more" class="public-search-more" type="button" hidden>Mostrar más resultados</button>
  <noscript><p>Para consultar las explicaciones sin JavaScript, utiliza los recorridos por rol disponibles en esta página.</p></noscript>
</section>

<section id="orientacion" class="guidance" data-catalog-url="{{ '/mantenimiento/share_catalog.json' | relative_url }}" data-site-root="{{ '/' | absolute_url }}" aria-labelledby="guidance-invite-heading">
  <div class="guidance-invite">
    <div>
      <h3 id="guidance-invite-heading">¿No sabes por dónde empezar?</h3>
      <p>Te ayudamos a identificar qué modalidad de iskay.app puede corresponder a lo que quieres hacer.</p>
    </div>
    <button id="guidance-start" class="guidance-start" type="button" aria-expanded="false" aria-controls="guidance-panel">Recibir orientación</button>
  </div>
  <div id="guidance-panel" class="guidance-panel" hidden>
    <div class="guidance-panel-heading">
      <strong>Orientación breve</strong>
      <button id="guidance-close" class="guidance-close" type="button">Cerrar</button>
    </div>
    <p id="guidance-question" class="guidance-question" role="status" aria-live="polite" tabindex="-1"></p>
    <div id="guidance-options" class="guidance-options"></div>
    <div id="guidance-result" class="guidance-result"></div>
    <div class="guidance-navigation">
      <button id="guidance-back" type="button" hidden>Volver</button>
      <button id="guidance-restart" type="button" hidden>Empezar de nuevo</button>
    </div>
    <p class="guidance-privacy">Sin registro ni datos personales. Tus respuestas no se guardan.</p>
  </div>
</section>

<script src="{{ '/assets/js/public-search.js' | relative_url }}?v=20261102-estandar" defer></script>
<script src="{{ '/assets/js/guidance.js' | relative_url }}?v=20261102-orientacion" defer></script>

<div class="fr-editorial-note">Publicación de prueba. Las fichas pendientes de revisión editorial conservan su aviso. Estamos validando la experiencia pública y móvil antes de integrar esta documentación al dominio institucional de iskay.app.</div>
