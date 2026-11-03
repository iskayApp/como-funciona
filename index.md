---
layout: default
title: "Cómo funciona · Financiamiento Reembolsable"
description: "Recorridos de Promotores, Inversores y Colaboradores de Financiamiento Reembolsable en iskay.app."
permalink: /
eyebrow: "Prueba de publicación · Revisión editorial por roles"
---

# Cómo funciona · Financiamiento Reembolsable

Consulta los recorridos de **Promotores, Inversores y Colaboradores** en Financiamiento Reembolsable.

<div class="test-note">
Estamos validando la experiencia pública y móvil antes de integrar esta documentación al dominio institucional de iskay.app.
</div>

## Elige tu rol

- [Promotores]({{ '/financiamiento-reembolsable/promotores/' | relative_url }}) — 33 fichas en seis etapas.
- [Inversores]({{ '/financiamiento-reembolsable/inversores/' | relative_url }}) — 37 fichas en siete etapas.
- [Colaboradores]({{ '/financiamiento-reembolsable/colaboradores/' | relative_url }}) — 29 fichas de base común y cuatro áreas de colaboración.

Los contenidos que aún requieren aprobación editorial están marcados como **pendientes de revisión**. Esta es una publicación de prueba y su contenido puede recibir ajustes.

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
  <noscript><p>Para consultar las explicaciones sin JavaScript, utiliza el recorrido por etapas que aparece a continuación.</p></noscript>
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

## Etapas para Promotores

<ul class="topic-list">
  <li>
    <a href="{{ '/financiamiento-reembolsable/promotores/antes-de-solicitar/' | relative_url }}">
      <span class="topic-number">Etapa 01 · Completa</span>
      <strong>Antes de solicitar</strong><br>
      Entiende qué es el financiamiento, quién puede solicitarlo, cómo revisar tu capacidad de reembolso y cómo definir el monto.
    </a>
  </li>
  <li>
    <a href="{{ '/financiamiento-reembolsable/promotores/configura-tu-financiamiento/' | relative_url }}">
      <span class="topic-number">Etapa 02 · Completa</span>
      <strong>Configura tu financiamiento</strong><br>
      Define el período y modalidad de campaña, plazo, TNA, pagos y garantías aplicables.
    </a>
  </li>
  <li>
    <a href="{{ '/financiamiento-reembolsable/promotores/prepara-la-revision-profesional/' | relative_url }}">
      <span class="topic-number">Etapa 03 · Completa</span>
      <strong>Prepara la revisión profesional</strong><br>
      Identifica qué colaboradores profesionales debes incorporar y qué revisión corresponde según el monto objetivo solicitado.
    </a>
  </li>
  <li>
    <a href="{{ '/financiamiento-reembolsable/promotores/construye-y-publica-tu-campana/' | relative_url }}">
      <span class="topic-number">Etapa 04 · Completa</span>
      <strong>Construye y publica tu campaña</strong><br>
      Prepara la descripción, contenido visual, documentación y condiciones de acceso para publicar tu campaña.
    </a>
  </li>
  <li>
    <a href="{{ '/financiamiento-reembolsable/promotores/cierre-formalizacion-transferencia/' | relative_url }}">
      <span class="topic-number">Etapa 05 · Completa</span>
      <strong>Cierre, formalización y transferencia</strong><br>
      Completa los requisitos posteriores al cierre antes de recibir los fondos.
    </a>
  </li>
  <li>
    <a href="{{ '/financiamiento-reembolsable/promotores/cumple-y-da-seguimiento/' | relative_url }}">
      <span class="topic-number">Etapa 06 · Completa</span>
      <strong>Cumple y da seguimiento</strong><br>
      Consulta el estado de las cuotas y conoce qué ocurre ante retrasos, mora o incumplimientos.
    </a>
  </li>
</ul>

## Recorrido de Promotores

**33 fichas desarrolladas y organizadas en 6 etapas.**
