/* La orientación usa el catálogo público, no solicita ni persiste datos personales. */
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
    this.attributes = {};
    this.hidden = false;
    this.textContent = "";
    this.href = "";
    this.focused = false;
  }
  appendChild(child) { this.children.push(child); return child; }
  replaceChildren(...children) { this.children = [...children]; }
  addEventListener(name, callback) { this.listeners[name] = callback; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  focus() { this.focused = true; }
  click() {
    assert.ok(this.listeners.click, "Debe existir un manejador de click");
    return this.listeners.click();
  }
}
const ids = ["guidance-start", "guidance-panel", "guidance-close",
  "guidance-question", "guidance-options", "guidance-result",
  "guidance-back", "guidance-restart"];

test("orientación sin datos personales hacia la ficha canónica publicada", async () => {
  const controls = Object.fromEntries(ids.map(id => ["#" + id, new FakeElement()]));
  const root = new FakeElement("section");
  root.dataset.siteRoot = "https://iskayapp.github.io/como-funciona/";
  root.dataset.catalogUrl = "/como-funciona/mantenimiento/share_catalog.json";
  root.querySelector = selector => controls[selector];
  const base = root.dataset.siteRoot;
  const common = {category: "Financiamiento Reembolsable", role: "Promotores", stage: "Antes de solicitar"};
  const items = [
    {...common, code: "FR-PRO-01", title: "¿Qué es el Financiamiento Reembolsable?",
      canonical_url: base + "financiamiento-reembolsable/promotores/antes-de-solicitar/que-es-el-financiamiento-reembolsable/",
      public_searchable: true},
    {...common, code: "PRIVADA", title: "Ficha no publicable",
      canonical_url: base + "privada/", public_searchable: false},
    {...common, code: "EXTERNA", title: "Ficha fuera del sitio",
      canonical_url: "https://example.org/fuera/", public_searchable: true},
  ];
  let requested = "";
  const source = fs.readFileSync(path.resolve(__dirname, "../assets/js/guidance.js"), "utf8");
  const document = {
    getElementById: id => id === "orientacion" ? root : null,
    createElement: tag => new FakeElement(tag)
  };
  vm.runInNewContext(source, {
    document, URL,
    fetch: async url => {
      requested = url;
      return {ok: true, json: async () => ({items})};
    }
  }, {filename: "guidance.js"});

  const options = controls["#guidance-options"];
  const question = controls["#guidance-question"];
  const choose = index => {
    assert.ok(options.children[index], "La opción elegida debe existir");
    options.children[index].click();
  };
  await controls["#guidance-start"].click();
  await new Promise(resolve => setImmediate(resolve));

  assert.equal(requested, root.dataset.catalogUrl, "Única fuente de fichas: catálogo existente");
  assert.equal(options.children.length, 3, "Preguntas conversacionales, sin formulario");
  assert.equal(controls["#guidance-start"].attributes["aria-expanded"], "true");
  choose(0); // Impulsar iniciativa
  assert.equal(options.children.length, 5, "Presentar las modalidades");
  choose(0); // Financiamiento Reembolsable
  assert.equal(options.children.length, 1, "Una etapa pública");
  choose(0); // Antes de solicitar
  assert.equal(options.children.length, 1, "No incluir enlaces externos o fichas privadas");
  choose(0); // Ficha canónica
  const links = controls["#guidance-result"].children.filter(child => child.tag === "a");
  assert.equal(links.length, 1);
  assert.equal(links[0].href, items[0].canonical_url);

  controls["#guidance-restart"].click();
  assert.equal(options.children.length, 3);
  choose(1); // Apoyar o invertir
  choose(0); // El único recorrido publicado pertenece a Promotores
  assert.match(question.textContent, /preparación/);
  assert.equal(controls["#guidance-result"].children.filter(child => child.tag === "a").length, 1);
  assert.equal(controls["#guidance-result"].children.find(child => child.tag === "a").href, "#buscar");
  controls["#guidance-back"].click();
  assert.equal(options.children.length, 5, "Volver a la pregunta anterior");
  controls["#guidance-close"].click();
  assert.equal(controls["#guidance-panel"].hidden, true);
  assert.equal(controls["#guidance-start"].attributes["aria-expanded"], "false");
});
