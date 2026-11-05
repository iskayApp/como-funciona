/* Orientación pública: decisiones breves, sin formularios ni datos personales.
 * Mismo catálogo canónico del buscador; no registra ni transmite respuestas.
 */
(() => {
  "use strict";
  const root = document.getElementById("orientacion");
  if (!root) return;
  const start = root.querySelector("#guidance-start");
  const panel = root.querySelector("#guidance-panel");
  const close = root.querySelector("#guidance-close");
  const question = root.querySelector("#guidance-question");
  const options = root.querySelector("#guidance-options");
  const result = root.querySelector("#guidance-result");
  const back = root.querySelector("#guidance-back");
  const restart = root.querySelector("#guidance-restart");
  const modes = [
    {id: "fr", label: "Financiamiento Reembolsable", detail: "Capital que se devuelve con intereses"},
    {id: "donacion", label: "Donación", detail: "Aportes sin obligación de devolución"},
    {id: "recompensa", label: "Recompensa", detail: "Aportes vinculados a recompensas"},
    {id: "precompra", label: "Precompra", detail: "Reservas o compras anticipadas"},
    {id: "acciones", label: "Inversión en Acciones", detail: "Participación mediante acciones"}
  ];
  const siteRoot = new URL(root.dataset.siteRoot);
  const normalize = value => String(value || "").normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("es").trim();
  let entries = [];
  let loaded = false;
  let loading = null;
  let history = [];
  let state = {screen: "intent", intent: "", mode: "", role: "", stage: "", code: ""};

  function safeUrl(value) {
    if (typeof value !== "string") return "";
    try {
      const url = new URL(value);
      return (url.protocol === "https:" || url.protocol === "http:") &&
        url.origin === siteRoot.origin && url.pathname.startsWith(siteRoot.pathname)
        ? url.href : "";
    } catch (_error) {
      return "";
    }
  }

  function node(tag, className, value) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (value !== undefined) el.textContent = String(value);
    return el;
  }

  function button(label, description, action) {
    const el = node("button", "guidance-choice");
    el.type = "button";
    el.appendChild(node("strong", "", label));
    if (description) el.appendChild(node("span", "", description));
    el.addEventListener("click", action);
    options.appendChild(el);
  }

  function go(next) {
    history.push({...state});
    state = {...state, ...next};
    render();
    // La respuesta elegida se elimina al cambiar de pregunta. Mantener el
    // recorrido de teclado sobre la pregunta nueva y sus opciones.
    question.focus();
  }

  function matching() {
    return entries.filter(item => normalize(item.category) === normalize(state.mode) &&
      (!state.role || item.role === state.role));
  }

  function rolesFor(mode) {
    return [...new Set(entries.filter(item => normalize(item.category) === normalize(mode))
      .map(item => item.role).filter(Boolean))]
      .filter(role => state.intent === "impulsar" ? normalize(role).includes("promotor") :
        state.intent === "apoyar" ? !normalize(role).includes("promotor") : true)
      .sort((a, b) => a.localeCompare(b, "es"));
  }

  function selectMode(mode) {
    const roles = rolesFor(mode);
    if (!roles.length) return go({screen: "unavailable", mode, role: ""});
    if (roles.length === 1) return go({screen: "stage", mode, role: roles[0]});
    return go({screen: "role", mode, role: ""});
  }

  function showMessage(message) {
    result.appendChild(node("p", "guidance-message", message));
  }

  function render() {
    options.replaceChildren();
    result.replaceChildren();
    back.hidden = history.length === 0;
    restart.hidden = history.length === 0;
    const screen = state.screen;
    if (screen === "intent") {
      question.textContent = "¿Qué te gustaría hacer?";
      button("Impulsar una iniciativa", "Quiero conseguir recursos para un proyecto",
        () => go({screen: "mode", intent: "impulsar"}));
      button("Apoyar o invertir en una iniciativa", "Quiero conocer cómo participar",
        () => go({screen: "mode", intent: "apoyar"}));
      button("Explorar las explicaciones disponibles", "Quiero descubrir los temas ya publicados",
        () => go({screen: "mode", intent: "explorar"}));
    } else if (screen === "mode") {
      question.textContent = state.intent === "explorar"
        ? "¿Sobre qué categoría te gustaría aprender?"
        : "¿Qué tipo de participación o financiación te interesa?";
      const available = [...new Set(entries.map(item => item.category))].filter(Boolean);
      const choices = state.intent === "explorar"
        ? available.map(name => ({label: name, detail: ""}))
        : modes;
      choices.forEach(item => button(item.label, item.detail, () => selectMode(item.label)));
      if (!choices.length) showMessage("Todavía no hay explicaciones disponibles.");
    } else if (screen === "role") {
      question.textContent = "¿Desde qué rol quieres consultar las explicaciones?";
      rolesFor(state.mode).forEach(role =>
        button(role, "", () => go({screen: "stage", role})));
    } else if (screen === "stage") {
      question.textContent = "¿En qué parte del proceso tienes dudas?";
      const stages = [...new Set(matching().map(item => item.stage).filter(Boolean))];
      stages.forEach(stage => button(stage, "", () => go({screen: "topic", stage})));
      if (!stages.length) showMessage("No hay etapas publicadas para esta opción.");
    } else if (screen === "topic") {
      question.textContent = "¿Qué te gustaría entender?";
      matching().filter(item => item.stage === state.stage)
        .sort((a, b) => String(a.code).localeCompare(String(b.code), "es", {numeric: true}))
        .forEach(item => button(item.title, "", () => go({screen: "result", code: item.code})));
    } else if (screen === "result") {
      question.textContent = "Aquí tienes la explicación correspondiente";
      const item = matching().find(entry => entry.code === state.code);
      if (item) {
        const link = node("a", "guidance-canonical-link", item.title);
        link.href = safeUrl(item.canonical_url);
        result.appendChild(link);
        const context = [item.category, item.role, item.stage].filter(Boolean).join(" · ");
        result.appendChild(node("p", "guidance-context", context));
        showMessage("Consulta la ficha canónica para conocer la explicación completa.");
      } else {
        showMessage("Esta ficha ya no está disponible. Puedes consultar el buscador.");
      }
    } else if (screen === "unavailable") {
      question.textContent = "Este recorrido está en preparación";
      showMessage("Todavía no hay fichas canónicas públicas para esta categoría y forma de participación. No te mostraremos contenido de otro recorrido como si correspondiera al tuyo.");
      const link = node("a", "guidance-search-link", "Ir al buscador");
      link.href = "#buscar";
      result.appendChild(link);
    }
  }

  async function openPanel() {
    panel.hidden = false;
    start.setAttribute("aria-expanded", "true");
    if (!loaded) {
      question.textContent = "Consultando las fichas disponibles…";
      options.replaceChildren();
      result.replaceChildren();
      if (!loading) {
        loading = fetch(root.dataset.catalogUrl, {cache: "no-store"})
          .then(response => {
            if (!response.ok) throw new Error("HTTP " + response.status);
            return response.json();
          })
          .then(data => {
            if (!data || !Array.isArray(data.items)) throw new Error("Catálogo inválido");
            entries = data.items.filter(item => item.public_searchable !== false &&
              item.title && item.category && item.role && safeUrl(item.canonical_url));
            loaded = true;
          })
          .catch(() => {
            question.textContent = "La orientación no está disponible por ahora.";
            showMessage("Puedes seguir utilizando el buscador y la navegación por etapas.");
          })
          .finally(() => { loading = null; });
      }
      await loading;
    }
    if (loaded && !panel.hidden) render();
    if (!panel.hidden) question.focus();
  }

  start.addEventListener("click", openPanel);
  close.addEventListener("click", () => {
    panel.hidden = true;
    start.setAttribute("aria-expanded", "false");
    start.focus();
  });
  back.addEventListener("click", () => {
    if (!history.length) return;
    state = history.pop();
    render();
    question.focus();
  });
  restart.addEventListener("click", () => {
    history = [];
    state = {screen: "intent", intent: "", mode: "", role: "", stage: "", code: ""};
    render();
    question.focus();
  });
})();
