/* Copia enlaces ya resueltos desde metadatos por Jekyll.
   No construye URLs manualmente ni depende de una categoría o rol. */
(function () {
  "use strict";

  function fallbackCopy(value) {
    var previousFocus = document.activeElement;
    var field = document.createElement("textarea");
    field.value = value;
    field.setAttribute("readonly", "");
    field.style.position = "fixed";
    field.style.top = "0";
    field.style.opacity = "0";
    document.body.appendChild(field);
    try {
      field.focus();
      field.select();
      if (!document.execCommand("copy")) throw new Error("No se pudo acceder al portapapeles");
    } finally {
      document.body.removeChild(field);
      if (previousFocus && typeof previousFocus.focus === "function") previousFocus.focus();
    }
  }

  async function copyText(value) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(value);
        return;
      } catch (error) {
        // Algunos navegadores móviles requieren el mecanismo alternativo.
      }
    }
    fallbackCopy(value);
  }

  document.addEventListener("click", async function (event) {
    var button = event.target.closest("[data-copy-target]");
    if (!button || button.disabled) return;

    var target = document.getElementById(button.dataset.copyTarget);
    var feedback = document.getElementById("copy-feedback");
    if (!target || !target.href) return;

    try {
      await copyText(target.href);
      if (feedback) feedback.textContent = "Enlace copiado al portapapeles.";
    } catch (error) {
      if (feedback) feedback.textContent = "No se pudo copiar. Abre «Ver destino» para copiar la dirección manualmente.";
    }
  });
})();
