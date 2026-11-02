/* Prueba de interacción sin dependencias externas para el buscador público. */
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

class FakeElement {
  constructor(tag = "div") {
    this.tag = tag;
    this.children = [];
    this.listeners = {};
    this.dataset = {};
    this.value = "";
    this.disabled = false;
    this.hidden = false;
    this.textContent = "";
    this.href = "";
    this.options = [];
  }
  addEventListener(name, callback) { this.listeners[name] = callback; }
  dispatch(name) {
    assert.ok(this.listeners[name], "Evento " + name + " sin manejar");
    return this.listeners[name]();
  }
  appendChild(child) {
    if (child.tag === "fragment") this.children.push(...child.children);
    else this.children.push(child);
    return child;
  }
  replaceChildren(...children) {
    this.children = [];
    children.forEach(child => this.appendChild(child));
    if (this.tag === "select") {
      this.options = [...this.children];
      this.value = this.options[0]?.value || "";
    }
  }
  add(option) {
    this.options.push(option);
    this.children.push(option);
  }
  focus() { this.focused = true; }
}

test("carga vacía, búsqueda acotada, paginación, enlaces seguros y limpiar filtros", async () => {
  const controls = {};
  for (const id of ["public-search-query", "public-search-category",
    "public-search-role", "public-search-clear", "public-search-results",
    "public-search-count", "public-search-more"]) {
    controls["#" + id] = new FakeElement(id.includes("category") || id.includes("role") ? "select" : "div");
  }
  const root = new FakeElement("section");
  root.dataset.siteRoot = "https://iskayapp.github.io/como-funciona/";
  root.dataset.catalogUrl = "/como-funciona/mantenimiento/share_catalog.json";
  root.querySelector = selector => controls[selector];

  const items = Array.from({length: 9}, (_, index) => ({
    code: "FR-PRO-" + String(index + 1).padStart(2, "0"),
    title: "¿Qué garantías necesita la iniciativa? " + (index + 1),
    category: "Financiamiento Reembolsable",
    role: "Promotores",
    stage: "Antes de solicitar",
    public_searchable: true,
    canonical_url: "https://iskayapp.github.io/como-funciona/tema-" + (index + 1) + "/",
  }));
  items.push({...items[0], code: "PRIVATE", public_searchable: false});
  items.push({...items[0], code: "INVALID", canonical_url: "https://example.org/fuera/"});

  const document = {
    getElementById(id) { return id === "buscar" ? root : null; },
    createElement(tag) { return new FakeElement(tag); },
    createDocumentFragment() { return new FakeElement("fragment"); },
  };
  class Option extends FakeElement {
    constructor(label, value) {
      super("option");
      this.textContent = label;
      this.value = value;
    }
  }

  const source = fs.readFileSync(path.resolve(__dirname, "../assets/js/public-search.js"), "utf8");
  vm.runInNewContext(source, {
    document, Option, URL,
    fetch: async () => ({ok: true, json: async () => ({items})}),
  }, {filename: "public-search.js"});
  await new Promise(resolve => setImmediate(resolve));

  const results = controls["#public-search-results"];
  const query = controls["#public-search-query"];
  const category = controls["#public-search-category"];
  const clear = controls["#public-search-clear"];
  const more = controls["#public-search-more"];
  assert.equal(query.disabled, false);
  assert.equal(results.children.length, 0, "La portada no debe listar 33 fichas sin buscar");
  assert.equal(more.hidden, true);
  assert.equal(category.options.length, 2, "Solo las categorías públicas y válidas");

  query.value = "garantias";
  query.dispatch("input");
  assert.equal(results.children.length, 6, "Mostrar solo seis resultados al inicio");
  assert.equal(more.hidden, false);
  more.dispatch("click");
  assert.equal(results.children.length, 9, "Mostrar resultados siguientes a petición");

  query.value = "FR-PRO-03";
  query.dispatch("input");
  assert.equal(results.children.length, 1, "Permitir encontrar el código de ficha");
  assert.equal(more.hidden, true);

  clear.dispatch("click");
  assert.equal(results.children.length, 0);
  assert.equal(category.value, "");
  assert.equal(query.value, "");
});
