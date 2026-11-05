"""Integration fixture for shared navigation; synthetic content is never published.

CI runs prepare, builds the isolated directory with Jekyll, then runs verify.
The optional smoke command exercises that same build with Playwright.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
import shutil

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = "/como-funciona"
DONOR = "/donacion/aportar/"  # Deliberately different from role.id = donantes.
COLLABORATOR = "/donacion/acompanar/"
STAGES = [DONOR + "comprender/", DONOR + "participar/"]
PUBLIC_CODES = ["FIX-DON-001", "FIX-DON-002"]
NONPUBLIC = [
    ("draft", {"status": "draft"}),
    ("review", {"status": "review"}),
    ("archived", {"status": "archived"}),
    ("private", {"visibility": "private"}),
    ("unpublished", {"published": False}),
]


def write_page(destination: Path, path: str, metadata: dict, body: str) -> None:
    target = destination / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("---\n" + yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False)
                      + "---\n\n" + body + "\n", encoding="utf-8")


def prepare(destination: Path) -> None:
    """Create a fresh, isolated source; never modify the real registry or fichas."""
    destination = destination.resolve()
    if destination == ROOT or ROOT.is_relative_to(destination):
        raise ValueError("El fixture requiere un directorio aislado, no el repositorio")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("El directorio de fixture debe estar vacío")
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("_includes", "_layouts", "assets"):
        shutil.copytree(ROOT / name, destination / name)
    (destination / "_data").mkdir()
    shutil.copy2(ROOT / "_data/visual.yml", destination / "_data/visual.yml")
    config = yaml.safe_load((ROOT / "_config.yml").read_text(encoding="utf-8"))
    config.update(url="https://example.test", baseurl=BASE, exclude=[])
    (destination / "_config.yml").write_text(yaml.safe_dump(config, allow_unicode=True), encoding="utf-8")
    categories = [
        {"id": "donacion", "name": "Donación", "url": "/donacion/", "status": "available", "roles": [
            {"id": "donantes", "name": "Donantes", "url": DONOR, "description": "Quiero aportar."},
            {"id": "promotores", "name": "Promotores", "url": "/donacion/promotores/", "description": "Solo borradores."},
            {"id": "colaboradores", "name": "Colaboradores", "url": COLLABORATOR, "description": "Quiero colaborar."},
            {"id": "privado", "name": "Rol privado", "url": "/donacion/privado/", "description": "Portada privada."},
        ]},
        {"id": "solo-borradores", "name": "Solo borradores", "url": "/solo-borradores/", "status": "available", "roles": [
            {"id": "lectores", "name": "Lectores", "url": "/solo-borradores/lectores/", "description": "Sin fichas públicas."},
        ]},
        {"id": "en-preparacion", "name": "En preparación", "url": "/en-preparacion/", "status": "preparation", "roles": [
            {"id": "lectores", "name": "Lectores", "url": "/en-preparacion/lectores/", "description": "Categoría pendiente."},
        ]},
    ]
    (destination / "_data/categories.yml").write_text(yaml.safe_dump(categories, allow_unicode=True, sort_keys=False), encoding="utf-8")
    write_page(destination, "index.md", {"layout": "default", "title": "Cómo funciona", "permalink": "/"},
               "# Prueba de navegación\n\n{% include home-routes.html %}\n{% include category-cards.html %}\n"
               '<section id="buscar"><h2>Buscar</h2></section><section id="orientacion"><h2>Orientación</h2></section>')

    for category in categories:
        write_page(destination, f"fixtures/{category['id']}/index.md", {
            "layout": "default", "title": category["name"], "category": category["name"], "permalink": category["url"],
        }, "# " + category["name"] + "\n\n{% include fr-context.html %}\n{% include fr-role-cards.html %}")
        for role in category["roles"]:
            metadata = {"layout": "default", "title": role["name"], "category": category["name"],
                        "role": role["name"], "permalink": role["url"]}
            if role["id"] == "privado":
                metadata["visibility"] = "private"
            write_page(destination, f"fixtures/{category['id']}/{role['id']}/index.md", metadata,
                       "{% include fr-context.html %}\n{% include fr-role-hub.html %}")

    def topic(path: str, code: str, title: str, category: str, role: str,
              stage: str, stage_url: str, **overrides) -> None:
        meta = {"layout": "default", "title": title, "category": category, "role": role,
                "stage": stage, "stage_url": stage_url, "permalink": stage_url + code.lower() + "/",
                "code": code, "status": "published", "published": True}
        meta.update(overrides)
        write_page(destination, path, meta, "# " + title + "\n\n## Respuesta breve\n\nContenido sintético de prueba.")

    for i, (stage, stage_url) in enumerate(zip(("Comprender", "Participar"), STAGES)):
        write_page(destination, f"fixtures/donacion/donantes/{i + 1}/index.md", {
            "layout": "default", "title": stage, "category": "Donación", "role": "Donantes", "permalink": stage_url,
        }, "# " + stage)
        topic(f"fixtures/donacion/donantes/{i + 1}/publica.md", PUBLIC_CODES[i],
              ("Primera explicación" if i == 0 else "Segunda explicación"), "Donación", "Donantes", stage, stage_url)
    for suffix, overrides in NONPUBLIC:
        topic(f"fixtures/donacion/donantes/1/{suffix}.md", "FIX-" + suffix.upper(),
              "Ficha oculta " + suffix, "Donación", "Donantes", "Comprender", STAGES[0], **overrides)
        topic(f"fixtures/solo-borradores/lectores/{suffix}.md", "FIX-ONLY-" + suffix.upper(),
              "Solo " + suffix, "Solo borradores", "Lectores", "Leer", "/solo-borradores/lectores/leer/", **overrides)
    topic("fixtures/donacion/promotores/draft.md", "FIX-PRO-DRAFT", "Promotor borrador",
          "Donación", "Promotores", "Preparar", "/donacion/promotores/preparar/", status="draft")
    topic("fixtures/donacion/privado/publica.md", "FIX-PRIVATE-HUB", "Portada privada",
          "Donación", "Rol privado", "Consultar", "/donacion/privado/consultar/")
    write_page(destination, "fixtures/donacion/colaboradores/etapa.md", {
        "layout": "default", "title": "Colaborar", "category": "Donación", "role": "Colaboradores",
        "permalink": COLLABORATOR + "colaborar/",
    }, "# Colaborar")
    topic("fixtures/donacion/colaboradores/publica.md", "FIX-COL-001", "Colaboración de ejemplo",
          "Donación", "Colaboradores", "Colaborar", COLLABORATOR + "colaborar/")
    topic("fixtures/en-preparacion/lectores/publica.md", "FIX-PENDING", "Categoría pendiente",
          "En preparación", "Lectores", "Leer", "/en-preparacion/lectores/leer/")
    print(f"PASS: fixture aislado de navegación preparado en {destination}")


@dataclass
class Element:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def all(self):
        yield self
        for child in self.children:
            if isinstance(child, Element):
                yield from child.all()

    @property
    def text(self):
        return "".join(child.text if isinstance(child, Element) else child for child in self.children)

    def having_class(self, name: str):
        return [node for node in self.all() if name in node.attrs.get("class", "").split()]


class Document(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, path: Path):
        super().__init__(convert_charrefs=True)
        self.root = Element("document")
        self.stack = [self.root]
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        node = Element(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                self.stack = self.stack[:index]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def links(node: Element):
    return [item.attrs.get("href", "") for item in node.all() if item.tag == "a"]


def verify(site: Path) -> None:
    def read(route):
        return Document(site / route.strip("/") / "index.html").root

    home = read("/")
    category = read("/donacion/")
    donor = read(DONOR)
    topic = read(STAGES[0] + PUBLIC_CODES[0].lower() + "/")
    stage = read(STAGES[0])
    collaborator = read(COLLABORATOR)
    expected_roles = [BASE + DONOR, BASE + COLLABORATOR]

    assert [node.text.strip() for node in donor.all() if node.tag == "h1"] == ["Donantes"]
    assert donor.having_class("fr-overline")[0].text.strip() == "Donación"
    assert donor.having_class("page-hub"), "La portada no FR debe recibir la presentación de recorrido"
    assert stage.having_class("page-stage"), "Las etapas no FR deben recibir su presentación"
    assert links(category.having_class("fr-role-grid")[0]) == expected_roles
    assert links(donor.having_class("fr-role-tabs")[0]) == expected_roles
    assert links(home.having_class("home-routes")[0]) == expected_roles
    assert [node.attrs["data-fr-code"] for node in donor.all() if "data-fr-code" in node.attrs] == PUBLIC_CODES
    assert [node.attrs["href"] for node in topic.having_class("breadcrumbs")[0].all() if node.tag == "a"] == [
        BASE + "/", BASE + "/donacion/", BASE + DONOR, BASE + STAGES[0],
    ]
    assert links(topic.having_class("fr-jump-panel")[0]) == [BASE + value for value in STAGES]
    assert links(topic.having_class("fr-context-actions")[0])[0] == BASE + DONOR
    assert any(node.attrs.get("src", "").startswith(BASE + "/assets/js/fr-explorer.js") for node in donor.all())
    assert collaborator.having_class("fr-hub")[0].attrs["data-section-layout"] == "stages"
    assert "Base común" not in collaborator.having_class("fr-hub")[0].text
    assert "áreas de colaboración" not in collaborator.having_class("fr-hub")[0].text

    for page in (home, category, donor, topic, stage, collaborator):
        for href in links(page):
            assert "/financiamiento-reembolsable/" not in href, href
            assert "/donacion/donantes/" not in href, "Se debe utilizar role.url, no construirlo con role.id"
            assert "/donacion/promotores/" not in href, "No enlazar recorridos compuestos solo por borradores"
            assert "/donacion/privado/" not in href, "No enlazar portadas de rol privadas"
            assert not any("fix-" + suffix in href for suffix, _ in NONPUBLIC), href
    for category_id in ("solo-borradores", "en-preparacion"):
        card = next(node for node in home.all() if node.attrs.get("data-category") == category_id)
        assert card.attrs["data-availability"] == "preparation"
        assert links(card) == [], "No activar categorías pendientes o sin fichas públicas"
        menu = next(node for node in home.all() if node.attrs.get("data-menu-category") == category_id)
        assert links(menu) == []
        landing = read(f"/{category_id}/")
        assert "Esta categoría está en preparación" in landing.text
        assert not landing.having_class("fr-role-card")
        hub = read(f"/{category_id}/lectores/")
        assert "Este recorrido está en preparación" in hub.text
        assert not hub.having_class("fr-start")
        assert not [node for node in hub.all() if "data-fr-topic" in node.attrs]
    print("PASS: Donación/Donantes, URLs del registro, roles, etapas, breadcrumbs, filtros de publicación y categorías pendientes")


def smoke(site: Path) -> None:
    import os
    from functools import partial
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread
    from playwright.sync_api import sync_playwright, expect

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith(BASE + "/"):
                self.path = self.path[len(BASE):]
            super().do_GET()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(site.resolve())))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=os.environ.get("CHROMIUM_EXECUTABLE_PATH"))
            page = browser.new_page(viewport={"width": 390, "height": 844})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(origin + BASE + DONOR)
            expect(page.locator("[data-fr-filter]")).to_be_visible()
            page.locator("[data-fr-filter-query]").fill("segunda")
            expect(page.locator("[data-fr-topic]:visible")).to_have_count(1)
            expect(page.locator("[data-fr-topic]:visible")).to_have_attribute("data-fr-code", PUBLIC_CODES[1])
            page.locator("[data-fr-filter-clear]").click()
            assert page.locator("[data-fr-filter-query]").evaluate("el => el === document.activeElement")
            assert page.locator("[data-fr-filter-section] option").count() == 3
            page.locator(".fr-role-tabs a").filter(has_text="Colaboradores").click()
            expect(page.locator("h1")).to_have_text("Colaboradores")
            assert page.locator("[data-fr-filter-section] optgroup").count() == 0
            page.locator(".fr-menu > summary").focus()
            page.keyboard.press("Enter")
            assert page.locator(".fr-menu").evaluate("el => el.open")
            page.keyboard.press("Escape")
            assert not page.locator(".fr-menu").evaluate("el => el.open")
            assert not errors, errors
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")
            browser.close()
    finally:
        server.shutdown()
    print("PASS: Donantes y Colaboradores no FR, búsqueda local, filtro de etapas, teclado y móvil")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "verify", "smoke"))
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    {"prepare": prepare, "verify": verify, "smoke": smoke}[args.command](args.directory)


if __name__ == "__main__":
    main()
