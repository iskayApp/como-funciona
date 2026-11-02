/* Buscador público de Cómo funciona.
 * Reutiliza el catálogo canónico del mantenimiento; presenta solo metadatos funcionales.
 */
(() => {
  "use strict";
  const root = document.getElementById("buscar");
  if (!root) return;

  const input = root.querySelector("#public-search-query");
  const category = root.querySelector("#public-search-category");
  const role = root.querySelector("#public-search-role");
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
      if (url.origin !== base.origin || !url.pathname.startsWith(base.pathname)) return "";
      if (url.protocol !== "https:" && url.protocol !== "http:") return "";
      return url.href;
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
    render(true);
  }

  function score(item, query) {
    if (!query) return 0;
    const code = normalize(item.code);
    const title = normalize(item.title);
    const stage = normalize(item.stage);
    if (code === query || title === query) return 100;
    if (title.startsWith(query)) return 80;
    if (code.startsWith(query)) return 75;
    if (title.includes(query)) return 65;
    if (stage.includes(query)) return 40;
    return 10;
  }

  function match(item, tokens) {
    const fields = [item.title, item.code, item.category, item.role, item.stage];
    const haystack = normalize(fields.filter(Boolean).join(" "));
    return tokens.every(token => haystack.includes(token));
  }

  function resultCard(item) {
    const article = element("article", "public-search-result");
    const url = safeCanonicalUrl(item.canonical_url);
    const heading = element("h3", "public-search-result-title");
    const link = element("a", "public-search-result-link", item.title || "Explicación");
    link.href = url;
    heading.appendChild(link);
    article.appendChild(heading);
    article.appendChild(element("p", "public-search-result-context",
      [item.category, item.role, item.stage].filter(Boolean).join(" · ")));
    const footer = element("div", "public-search-result-footer");
    if (item.code) footer.appendChild(element("span", "public-search-code", "Ficha " + item.code));
    const action = element("a", "public-search-open", "Leer explicación");
    action.href = url;
    footer.appendChild(action);
    article.appendChild(footer);
    return article;
  }

  function render(resetLimit) {
    if (resetLimit) visibleLimit = pageSize;
    const query = normalize(input.value);
    const hasCriteria = Boolean(query || category.value || role.value);
    if (!hasCriteria) {
      count.textContent = "Escribe lo que necesitas saber o elige un filtro.";
      results.replaceChildren();
      more.hidden = true;
      return;
    }

    const tokens = query ? query.split(/\s+/).filter(Boolean) : [];
    const found = items.filter(item =>
      (!category.value || item.category === category.value) &&
      (!role.value || item.role === role.value) &&
      match(item, tokens));
    if (query) found.sort((a, b) => score(b, query) - score(a, query));

    const visible = found.slice(0, visibleLimit);
    const fragment = document.createDocumentFragment();
    if (!found.length) {
      fragment.appendChild(element("p", "public-search-empty",
        "No encontramos una explicación con esos criterios. Prueba con otras palabras o explora las etapas."));
    } else {
      visible.forEach(item => fragment.appendChild(resultCard(item)));
    }
    results.replaceChildren(fragment);
    count.textContent = found.length
      ? ("Mostrando " + visible.length + " de " + found.length +
        (found.length === 1 ? " explicación encontrada" : " explicaciones encontradas"))
      : "Sin resultados";
    more.hidden = visible.length >= found.length;
  }

  input.addEventListener("input", () => render(true));
  category.addEventListener("change", updateRoles);
  role.addEventListener("change", () => render(true));
  clear.addEventListener("click", () => {
    input.value = "";
    category.value = "";
    updateRoles();
    role.value = "";
    render(true);
    input.focus();
  });
  more.addEventListener("click", () => {
    visibleLimit += pageSize;
    render(false);
  });

  fetch(root.dataset.catalogUrl, { cache: "no-store" })
    .then(response => {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.json();
    })
    .then(data => {
      if (!data || !Array.isArray(data.items)) throw new Error("Formato de catálogo inválido");
      items = data.items.filter(item =>
        item.public_searchable !== false &&
        item.title &&
        safeCanonicalUrl(item.canonical_url));
      fillOptions(category, items.map(item => item.category), "Todas las categorías");
      updateRoles();
      category.disabled = false;
      role.disabled = false;
      input.disabled = false;
      clear.disabled = false;
      count.textContent = "Escribe lo que necesitas saber o elige un filtro.";
    })
    .catch(_error => {
      count.textContent = "No se pudo cargar la búsqueda. Puedes navegar por las etapas disponibles.";
      results.replaceChildren();
      more.hidden = true;
      input.disabled = true;
      category.disabled = true;
      role.disabled = true;
      clear.disabled = true;
    });
})();
