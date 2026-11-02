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

  function linkActions(canonicalUrl, asset) {
    const actions = node("div", "maint-search-buttons");
    actions.appendChild(copyButton("Copiar ficha", canonicalUrl));
    actions.appendChild(copyButton("Copiar multimedia", asset && asset.media_url,
      "El recurso no está insertado en la ficha"));
    actions.appendChild(copyButton("Copiar original", asset && asset.original_url,
      "No consta una URL verificable de la publicación o archivo original"));
    return actions;
  }

  function assetRow(asset, canonicalUrl) {
    const row = node("div", "maint-search-piece maint-search-asset");
    const label = asset.provider || asset.type || "Recurso";
    row.appendChild(node("h5", "maint-search-piece-title", label + " · " + (asset.title || asset.id || "Sin título")));
    row.appendChild(node("p", "maint-search-meta", "ID técnico: " + (asset.id || "Sin ID") +
      (asset.media_url ? " · Multimedia dentro de la ficha" : " · Publicación distribuida")));
    row.appendChild(linkActions(canonicalUrl, asset));
    return row;
  }

  function resultCard(item) {
    const card = node("article", "maint-search-result");
    card.appendChild(node("p", "maint-search-ficha-code", "Ficha canónica · " + (item.code || "Sin código")));
    card.appendChild(node("h3", "maint-search-heading", item.title || "Sin título"));
    card.appendChild(node("p", "maint-search-meta", [item.category, item.role, item.stage].filter(Boolean).join(" · ")));

    // Sólo los metadatos editoriales explícitos crean una relación con la producción.
    const linkedPieces = Array.isArray(item.marketing_pieces) ? item.marketing_pieces : [];
    const fallbackAssets = [...(Array.isArray(item.media) ? item.media : []),
      ...(Array.isArray(item.distribution) ? item.distribution : [])];
    const unassigned = Array.isArray(item.unassigned_assets) ? item.unassigned_assets : fallbackAssets;

    card.appendChild(node("p", "maint-search-meta", linkedPieces.length
      ? linkedPieces.length + (linkedPieces.length === 1 ? " pieza publicitaria vinculada" : " piezas publicitarias vinculadas")
      : "Sin pieza publicitaria identificada en los metadatos"));

    linkedPieces.forEach(piece => {
      const group = node("section", "maint-search-piece maint-search-production");
      const officialCode = (piece.code || "Sin código") +
        (piece.category_code ? " (" + piece.category_code + ")" : "");
      group.appendChild(node("h4", "maint-search-piece-title", "Pieza publicitaria · " + officialCode));
      group.appendChild(node("p", "maint-search-meta", piece.title || "Título no registrado"));
      const assets = Array.isArray(piece.assets) ? piece.assets : [];
      if (!assets.length) {
        group.appendChild(node("p", "maint-search-empty", "Aún no hay publicaciones aprobadas vinculadas a esta pieza."));
        group.appendChild(linkActions(item.canonical_url, null));
      } else {
        assets.forEach(asset => group.appendChild(assetRow(asset, item.canonical_url)));
      }
      card.appendChild(group);
    });

    if (unassigned.length) {
      const group = node("section", "maint-search-piece maint-search-unassigned");
      group.appendChild(node("h4", "maint-search-piece-title", "Recursos y publicaciones sin pieza publicitaria identificada"));
      group.appendChild(node("p", "maint-search-meta", "Se conserva su vínculo con la ficha, pero no se presupone un código de producción."));
      unassigned.forEach(asset => group.appendChild(assetRow(asset, item.canonical_url)));
      card.appendChild(group);
    } else if (!linkedPieces.length) {
      card.appendChild(node("p", "maint-search-empty", "Esta ficha no tiene publicaciones aprobadas asociadas."));
      card.appendChild(linkActions(item.canonical_url, null));
    }
    return card;
  }

  function matches(item, query, cat, selectedRole) {
    if (cat && item.category !== cat) return false;
    if (selectedRole && item.role !== selectedRole) return false;
    if (!query) return true;
    const pieces = [...(Array.isArray(item.media) ? item.media : []),
      ...(Array.isArray(item.distribution) ? item.distribution : [])];
    const marketing = Array.isArray(item.marketing_pieces) ? item.marketing_pieces : [];
    const haystack = normalize([
      item.code, item.title, item.category, item.role, item.stage,
      ...marketing.flatMap(piece => [piece.code, piece.title, piece.category_code]),
      ...pieces.flatMap(piece => [piece.title, piece.id, piece.provider, piece.type])
    ].filter(Boolean).join(" "));
    return normalize(query).split(/\s+/).every(token => haystack.includes(token));
  }

  function render() {
    const hasCriteria = Boolean(normalize(search.value) || category.value || role.value);
    if (!hasCriteria) {
      // No mostrar el catálogo completo por defecto: la vista es un buscador, no un listado.
      results.replaceChildren();
      count.textContent = "Escribe un concepto o selecciona un filtro para buscar.";
      feedback.textContent = "";
      return;
    }

    const found = items.filter(item => matches(item, search.value, category.value, role.value));
    count.textContent = found.length + (found.length === 1 ? " ficha encontrada" : " fichas encontradas");
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
