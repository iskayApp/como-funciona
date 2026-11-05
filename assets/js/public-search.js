/* Buscador público de Cómo funciona: una barra y filtros progresivos.
 * Fuente única: catálogo canónico compartido con mantenimiento.
 */
(() => {
  "use strict";
  const root = document.getElementById("buscar");
  if (!root) return;

  const form = root.querySelector("#public-search-form");
  const input = root.querySelector("#public-search-query");
  const submit = root.querySelector("#public-search-submit");
  const tools = root.querySelector("#public-search-tools");
  const toggle = root.querySelector("#public-search-filter-toggle");
  const filters = root.querySelector("#public-search-filters");
  const category = root.querySelector("#public-search-category");
  const role = root.querySelector("#public-search-role");
  const stageFilter = root.querySelector("#public-search-stage");
  const typeFilter = root.querySelector("#public-search-type");
  const typeLabels = {ficha: "Ficha canónica", diagram: "Diagrama", animation: "Animación", image: "Imagen", video: "Video", audio: "Audio"};
  const clear = root.querySelector("#public-search-clear");
  const results = root.querySelector("#public-search-results");
  const count = root.querySelector("#public-search-count");
  const more = root.querySelector("#public-search-more");
  const pageSize = 6;
  let visibleLimit = pageSize;
  let items = [];

  const normalize = value => String(value ?? "").normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("es").trim();

  function element(tag, className, content) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (content !== undefined) node.textContent = String(content);
    return node;
  }

  function safeCanonicalUrl(value) {
    if (typeof value !== "string") return "";
    try {
      const base = new URL(root.dataset.siteRoot);
      const url = new URL(value);
      return ["https:", "http:"].includes(url.protocol) &&
        url.origin === base.origin && url.pathname.startsWith(base.pathname)
        ? url.href : "";
    } catch (_error) {
      return "";
    }
  }

  function fillOptions(select, values, allLabel) {
    select.replaceChildren(new Option(allLabel, ""));
    [...new Set(values.filter(Boolean).map(String))]
      .sort((a, b) => a.localeCompare(b, "es"))
      .forEach(value => select.add(new Option(value, value)));
  }

  function updateRoles() {
    const previous = role.value;
    const scoped = category.value ? items.filter(item => item.category === category.value) : items;
    fillOptions(role, scoped.map(item => item.role), "Todos los roles");
    if ([...role.options].some(option => option.value === previous)) role.value = previous;
    updateStages();
  }

  function scopedItems() {
    return items.filter(item => (!category.value || item.category === category.value) &&
      (!role.value || item.role === role.value));
  }

  function updateTypes() {
    if (!typeFilter) return;
    const previous = typeFilter.value;
    const scoped = scopedItems().filter(item => !stageFilter?.value || item.stage === stageFilter.value);
    const types = [...new Set(scoped.flatMap(item => (item.media || []).map(media => media.type)).filter(Boolean))];
    typeFilter.replaceChildren(new Option("Todos los tipos", ""));
    if (scoped.length) typeFilter.add(new Option("Ficha canónica", "ficha"));
    types.sort().forEach(value => typeFilter.add(new Option(typeLabels[value] || value, value)));
    if ([...typeFilter.options].some(option => option.value === previous)) typeFilter.value = previous;
  }

  function updateStages() {
    if (stageFilter) {
      const previous = stageFilter.value;
      fillOptions(stageFilter, scopedItems().map(item => item.stage), "Todas las etapas");
      if ([...stageFilter.options].some(option => option.value === previous)) stageFilter.value = previous;
    }
    updateTypes();
    render(true);
  }

  function score(item, query) {
    if (!query) return 0;
    const code = normalize(item.code), title = normalize(item.title), stage = normalize(item.stage);
    if (title === query || code === query) return 100;
    if (title.startsWith(query)) return 80;
    if (code.startsWith(query)) return 75;
    if (title.includes(query)) return 65;
    if (stage.includes(query)) return 40;
    return 10;
  }

  function match(item, tokens) {
    const haystack = normalize([item.title, item.code, item.category, item.role, item.stage]
      .filter(Boolean).join(" "));
    return tokens.every(token => haystack.includes(token));
  }

  function resultCard(item) {
    const url = safeCanonicalUrl(item.canonical_url);
    const link = element("a", "public-search-result");
    link.href = url;

    const text = element("span", "public-search-result-content");
    text.appendChild(element("strong", "public-search-result-title", item.title || "Explicación"));
    text.appendChild(element("span", "public-search-result-context",
      [item.category, item.role, item.stage].filter(Boolean).join(" · ")));
    link.appendChild(text);
    link.appendChild(element("span", "public-search-result-arrow", "›"));
    return link;
  }

  function render(resetLimit) {
    if (resetLimit) visibleLimit = pageSize;
    const query = normalize(input.value);
    const hasCriteria = Boolean(query || category.value || role.value || stageFilter?.value || typeFilter?.value);
    tools.hidden = !hasCriteria;

    if (!hasCriteria) {
      filters.hidden = true;
      toggle.setAttribute("aria-expanded", "false");
      count.textContent = "";
      results.replaceChildren();
      more.hidden = true;
      return;
    }

    const tokens = query.split(/\s+/).filter(Boolean);
    const found = items.filter(item =>
      (!category.value || item.category === category.value) &&
      (!role.value || item.role === role.value) &&
      (!stageFilter?.value || item.stage === stageFilter.value) &&
      (!typeFilter?.value || typeFilter.value === "ficha" || (item.media || []).some(media => media.type === typeFilter.value)) && match(item, tokens));
    if (query) found.sort((a, b) => score(b, query) - score(a, query));

    const fragment = document.createDocumentFragment();
    found.slice(0, visibleLimit).forEach(item => fragment.appendChild(resultCard(item)));
    if (!found.length) {
      fragment.appendChild(element("p", "public-search-empty",
        "No encontramos una explicación. Prueba con otras palabras o modifica los filtros."));
    }
    results.replaceChildren(fragment);
    const showing = Math.min(found.length, visibleLimit);
    count.textContent = found.length
      ? (found.length === showing
          ? found.length + (found.length === 1 ? " resultado" : " resultados")
          : "Mostrando " + showing + " de " + found.length + " resultados")
      : "Sin resultados";
    more.hidden = showing >= found.length;
  }

  form.addEventListener("submit", event => {
    event.preventDefault();
    render(true);
  });
  // La búsqueda también responde mientras se escribe, sin obligar a pulsar el botón.
  input.addEventListener("input", () => render(true));
  category.addEventListener("change", updateRoles);
  role.addEventListener("change", updateStages);
  stageFilter?.addEventListener("change", () => { updateTypes(); render(true); });
  typeFilter?.addEventListener("change", () => render(true));

  toggle.addEventListener("click", () => {
    filters.hidden = !filters.hidden;
    toggle.setAttribute("aria-expanded", String(!filters.hidden));
    if (!filters.hidden) category.focus();
  });

  clear.addEventListener("click", () => {
    input.value = "";
    category.value = "";
    role.value = "";
    if (stageFilter) stageFilter.value = "";
    if (typeFilter) typeFilter.value = "";
    updateRoles();
    filters.hidden = true;
    toggle.setAttribute("aria-expanded", "false");
    render(true);
    input.focus();
  });

  more.addEventListener("click", () => {
    const firstNewIndex = visibleLimit;
    visibleLimit += pageSize;
    render(false);
    // Los enlaces nuevos aparecen antes del botón, que puede quedar oculto.
    // Continuar desde el primero de ellos sin reiniciar la navegación de teclado.
    results.children[firstNewIndex]?.focus();
  });

  fetch(root.dataset.catalogUrl, {cache: "no-store"})
    .then(response => {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.json();
    })
    .then(data => {
      if (!data || !Array.isArray(data.items)) throw new Error("Catálogo no válido");
      items = data.items.filter(item => item.public_searchable !== false &&
        item.title && safeCanonicalUrl(item.canonical_url));
      fillOptions(category, items.map(item => item.category), "Todas las categorías");
      updateRoles();
      input.disabled = false;
      submit.disabled = false;
      toggle.disabled = false;
      category.disabled = false;
      role.disabled = false;
      clear.disabled = false;
      if (stageFilter) stageFilter.disabled = false;
      if (typeFilter) typeFilter.disabled = false;
      render(true);
    })
    .catch(_error => {
      count.textContent = "La búsqueda no está disponible. Puedes navegar por las etapas.";
      tools.hidden = true;
      filters.hidden = true;
      results.replaceChildren();
      more.hidden = true;
      input.disabled = true;
      submit.disabled = true;
      toggle.disabled = true;
      category.disabled = true;
      role.disabled = true;
      clear.disabled = true;
      if (stageFilter) stageFilter.disabled = true;
      if (typeFilter) typeFilter.disabled = true;
    });
})();
