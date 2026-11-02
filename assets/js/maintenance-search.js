/* Buscador de marketing en el mantenimiento existente.
 * Consume exclusivamente el catálogo de enlaces ya generado por build_share_catalog.py.
 */
(() => {
  "use strict";
  const root = document.getElementById("maintenance-search");
  if (!root) return;

  const search = root.querySelector("#maint-search-text");
  const category = root.querySelector("#maint-search-category");
  const role = root.querySelector("#maint-search-role");
  const clear = root.querySelector("#maint-search-clear");
  const results = root.querySelector("#maint-search-results");
  const count = root.querySelector("#maint-search-count");
  const feedback = root.querySelector("#maint-search-feedback");
  let items = [];

  const normalize = value => String(value == null ? "" : value)
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("es").trim();

  const safeUrl = value => {
    if (typeof value !== "string") return "";
    try {
      const parsed = new URL(value);
      return (parsed.protocol === "https:" || parsed.protocol === "http:") && parsed.hostname ? parsed.href : "";
    } catch (_error) {
      return "";
    }
  };

  function node(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined && text !== null) element.textContent = String(text);
    return element;
  }

  function choiceOptions(select, values, defaultText) {
    select.replaceChildren(new Option(defaultText, ""));
    [...new Set(values.filter(Boolean).map(String))]
      .sort((a, b) => a.localeCompare(b, "es"))
      .forEach(value => select.add(new Option(value, value)));
  }

  async function copyToClipboard(value) {
    if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
      try {
        await navigator.clipboard.writeText(value);
        return true;
      } catch (_error) {
        // Navegadores sin permisos: continuar con la alternativa.
      }
    }
    const textarea = document.createElement("textarea");
    textarea.value = value;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    let success = false;
    try {
      success = document.execCommand("copy");
    } catch (_error) {
      success = false;
    }
    textarea.remove();
    return success;
  }

  function copyButton(label, value, unavailable) {
    const button = node("button", "maint-search-copy", label);
    button.type = "button";
    const url = safeUrl(value);
    if (!url) {
      button.disabled = true;
      button.title = unavailable || "Enlace no disponible en los metadatos aprobados";
    } else {
      button.dataset.copyUrl = url;
      button.setAttribute("aria-label", label);
    }
    return button;
  }

  function resultCard(item) {
    const card = node("article", "maint-search-result");
    const heading = node("h3", "maint-search-heading", (item.code || "Sin código") + " · " + (item.title || "Sin título"));
    card.appendChild(heading);
    const metadata = [item.category, item.role, item.stage].filter(Boolean).join(" · ");
    card.appendChild(node("p", "maint-search-meta", metadata));

    const pieces = [...(Array.isArray(item.media) ? item.media : []),
      ...(Array.isArray(item.distribution) ? item.distribution : [])];
    if (!pieces.length) {
      card.appendChild(node("p", "maint-search-empty", "Sin piezas publicables asociadas todavía."));
      const actions = node("div", "maint-search-buttons");
      actions.appendChild(copyButton("Copiar ficha", item.canonical_url));
      actions.appendChild(copyButton("Copiar multimedia", null, "Esta ficha todavía no tiene multimedia aprobada"));
      actions.appendChild(copyButton("Copiar original", null, "Esta ficha todavía no tiene recursos originales aprobados"));
      card.appendChild(actions);
      return card;
    }

    const summary = node("p", "maint-search-meta", pieces.length + (pieces.length === 1 ? " pieza asociada" : " piezas asociadas"));
    card.appendChild(summary);
    pieces.forEach(piece => {
      const row = node("div", "maint-search-piece");
      const title = piece.title || piece.id || "Recurso sin título";
      row.appendChild(node("h4", "maint-search-piece-title", title));
      const description = [piece.provider || piece.type || "Multimedia", piece.id || "", piece.media_url ? "Dentro de la ficha" : "Publicación distribuida"]
        .filter(Boolean).join(" · ");
      row.appendChild(node("div", "maint-search-meta", description));
      const actions = node("div", "maint-search-buttons");
      actions.appendChild(copyButton("Copiar ficha", item.canonical_url));
      actions.appendChild(copyButton("Copiar multimedia", piece.media_url, "Esta publicación no está insertada en la ficha"));
      actions.appendChild(copyButton("Copiar original", piece.original_url, "La publicación o el archivo de origen no tiene URL verificable"));
      row.appendChild(actions);
      card.appendChild(row);
    });
    return card;
  }

  function matches(item, query, cat, selectedRole) {
    if (cat && item.category !== cat) return false;
    if (selectedRole && item.role !== selectedRole) return false;
    if (!query) return true;
    const pieces = [...(Array.isArray(item.media) ? item.media : []),
      ...(Array.isArray(item.distribution) ? item.distribution : [])];
    const haystack = normalize([
      item.code, item.title, item.category, item.role, item.stage,
      ...pieces.flatMap(piece => [piece.title, piece.id, piece.provider, piece.type])
    ].filter(Boolean).join(" "));
    return normalize(query).split(/\s+/).every(token => haystack.includes(token));
  }

  function render() {
    const found = items.filter(item => matches(item, search.value, category.value, role.value));
    count.textContent = found.length + " de " + items.length + " fichas";
    const fragment = document.createDocumentFragment();
    if (!found.length) {
      fragment.appendChild(node("p", "maint-search-empty", "No hay fichas con estos criterios. Prueba con otro concepto, código, categoría o rol."));
    } else {
      found.forEach(item => fragment.appendChild(resultCard(item)));
    }
    results.replaceChildren(fragment);
  }

  function updateRoles() {
    const previous = role.value;
    const filtered = category.value ? items.filter(item => item.category === category.value) : items;
    choiceOptions(role, filtered.map(item => item.role), "Todos los roles");
    if ([...role.options].some(option => option.value === previous)) role.value = previous;
    render();
  }

  search.addEventListener("input", render);
  category.addEventListener("change", updateRoles);
  role.addEventListener("change", render);
  clear.addEventListener("click", () => {
    search.value = "";
    category.value = "";
    updateRoles();
    role.value = "";
    feedback.textContent = "";
    render();
    search.focus();
  });
  results.addEventListener("click", async event => {
    const button = event.target.closest("button[data-copy-url]");
    if (!button || !results.contains(button)) return;
    const success = await copyToClipboard(button.dataset.copyUrl);
    feedback.textContent = success
      ? "Enlace copiado: " + button.dataset.copyUrl
      : "No se pudo copiar automáticamente. Comprueba los permisos del portapapeles.";
  });

  fetch(root.dataset.catalogUrl, { cache: "no-store" })
    .then(response => {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.json();
    })
    .then(data => {
      if (!data || !Array.isArray(data.items)) throw new Error("Formato de catálogo no válido");
      items = data.items;
      choiceOptions(category, items.map(item => item.category), "Todas las categorías");
      updateRoles();
    })
    .catch(error => {
      count.textContent = "No disponible";
      results.replaceChildren(node("p", "maint-search-empty", "No se pudo cargar el catálogo de enlaces: " + error.message));
    });
})();
