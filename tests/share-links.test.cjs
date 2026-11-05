/* La copia alternativa conserva el teclado y limpia el campo incluso si falla. */
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(path.resolve(__dirname, "../assets/js/share-links.js"), "utf8");

async function copyWith({clipboard, execCommand}) {
  const temporaryFields = [];
  const feedback = {textContent: ""};
  const target = {href: "https://iskayapp.github.io/como-funciona/ficha/"};
  let listener;
  const document = {
    activeElement: null,
    addEventListener: (_name, callback) => { listener = callback; },
    getElementById: id => id === "share-ficha" ? target : feedback,
    createElement: () => ({
      style: {},
      setAttribute() {},
      select() {},
      focus() { document.activeElement = this; },
    }),
    execCommand,
    body: {
      appendChild(field) { temporaryFields.push(field); },
      removeChild(field) {
        temporaryFields.splice(temporaryFields.indexOf(field), 1);
        if (document.activeElement === field) document.activeElement = this;
      },
    },
  };
  const button = {
    dataset: {copyTarget: "share-ficha"},
    closest: () => button,
    focus() { document.activeElement = this; },
  };
  button.focus();
  vm.runInNewContext(source, {document, navigator: {clipboard}}, {filename: "share-links.js"});
  await listener({target: button});
  return {document, button, temporaryFields, feedback, target};
}

test("copia con Clipboard API y mantiene el foco del botón", async () => {
  let copied;
  const {document, button, feedback, target} = await copyWith({
    clipboard: {writeText: async value => { copied = value; }},
    execCommand: () => { throw new Error("No debe usar el mecanismo alternativo"); },
  });
  assert.equal(copied, target.href);
  assert.equal(document.activeElement, button);
  assert.match(feedback.textContent, /copiado/);
});

test("rechazo de Clipboard API: copia alternativa sin perder el foco", async () => {
  const {document, button, temporaryFields, feedback} = await copyWith({
    clipboard: {writeText: async () => { throw new Error("Permiso no disponible"); }},
    execCommand: () => true,
  });
  assert.equal(document.activeElement, button);
  assert.equal(temporaryFields.length, 0);
  assert.match(feedback.textContent, /copiado/);
});

test("fallo de copia alternativa: limpia el campo y devuelve el foco", async () => {
  for (const execCommand of [() => false, () => { throw new Error("No soportado"); }]) {
    const {document, button, temporaryFields, feedback} = await copyWith({execCommand});
    assert.equal(temporaryFields.length, 0, "No dejar campos invisibles en el documento");
    assert.equal(document.activeElement, button, "El usuario conserva su posición de teclado");
    assert.match(feedback.textContent, /No se pudo copiar/);
  }
});
