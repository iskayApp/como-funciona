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
    this.attributes = {};
    this.focused = false;
  }
  addEventListener(name, callback) { this.listeners[name] = callback; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  getAttribute(name) { return this.attributes[name]; }
  dispatch(name) {
    assert.ok(this.listeners[name], "Evento " + name + " sin manejar");
    return this.listeners[name]({ preventDefault() {} });
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
  for (const id of ["public-search-form", "public-search-query", "public-search-submit",
    "public-search-tools", "public-search-filter-toggle", "public-search-filters",
    "public-search-category", "public-search-role", "public-search-clear",
    "public-search-results", "public-search-count", "public-search-more"]) {
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
  const filters = controls["#public-search-filters"];
  const tools = controls["#public-search-tools"];
  const toggle = controls["#public-search-filter-toggle"];
  const role = controls["#public-search-role"];
  const form = controls["#public-search-form"];
  filters.hidden = true;
  tools.hidden = true;
  assert.equal(query.disabled, false);
  assert.equal(results.children.length, 0, "La portada no debe listar 33 fichas sin buscar");
  assert.equal(more.hidden, true);
  assert.equal(tools.hidden, true, "No mostrar filtros antes de buscar");
  assert.equal(filters.hidden, true);
  assert.equal(category.options.length, 2, "Solo las categorías públicas y válidas");

  query.value = "garantias";
  query.dispatch("input");
  assert.equal(results.children.length, 6, "Mostrar solo seis resultados al inicio");
  assert.equal(tools.hidden, false);
  assert.equal(filters.hidden, true, "Los filtros se despliegan a petición");
  toggle.dispatch("click");
  assert.equal(filters.hidden, false);
  assert.equal(toggle.getAttribute("aria-expanded"), "true");
  assert.equal(category.focused, true);
  category.value = "Financiamiento Reembolsable";
  category.dispatch("change");
  assert.equal(results.children.length, 6);
  assert.equal(role.options.length, 2);
  assert.ok(results.children[0].href.includes('/como-funciona/tema-'));
  category.value = "";
  category.dispatch("change");
  assert.equal(more.hidden, false);
  more.dispatch("click");
  assert.equal(results.children.length, 9, "Mostrar resultados siguientes a petición");

  query.value = "FR-PRO-03";
  form.dispatch("submit");
  query.dispatch("input");
  assert.equal(results.children.length, 1, "Permitir encontrar el código de ficha");
  assert.equal(more.hidden, true);

  clear.dispatch("click");
  assert.equal(results.children.length, 0);
  assert.equal(category.value, "");
  assert.equal(query.value, "");
  assert.equal(tools.hidden, true);
  assert.equal(filters.hidden, true);
  assert.equal(toggle.getAttribute("aria-expanded"), "false");
});
