"""Check the 40 published Donación fichas and their real Jekyll navigation.

Publication is authorized independently of editorial approval. Source metadata
continues to require pending_review and reviewed:false for all 60 pages.
Browser checks serve the built output locally, including canonical search links.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from urllib.parse import urlsplit

import yaml

from build_share_catalog import frontmatter
from check_category_navigation import Document, links
from check_site_integrity import audit as audit_integrity
from verify_maintenance_site import audit as audit_routes


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT
ROLES = {
    "PRO": {"id": "promotores", "name": "Promotores", "topics": 18, "stages": 7, "classification": 71},
    "DON": {"id": "donantes", "name": "Donantes", "topics": 14, "stages": 5, "classification": 42},
    "COL": {"id": "colaboradores", "name": "Colaboradores", "topics": 8, "stages": 4, "classification": 23},
}


def normalized(value):
    return " ".join(str(value).split())


def inventory(root: Path):
    """Derive titles, routes and stages from the real front matter, not a fixture catalog."""
    config = yaml.safe_load((root / "_config.yml").read_text(encoding="utf-8"))
    categories = yaml.safe_load((root / "_data/categories.yml").read_text(encoding="utf-8"))
    category = next(c for c in categories if c["id"] == "donacion")
    assert config.get("noindex") is True, "La publicación conserva noindex"
    assert category["status"] == "available"
    assert "ideas/donacion" not in config.get("exclude", [])
    assert category["url"] == "/donacion/"
    assert len(category["roles"]) == 3, "Se requieren exactamente tres roles"
    roles = {r["id"]: r for r in category["roles"]}
    assert set(roles) == {r["id"] for r in ROLES.values()}, "Se requieren los tres roles de Donación"
    assert len({r["url"] for r in roles.values()}) == 3, "Las rutas de roles deben ser únicas"

    pages, topics = {}, {}
    for path in sorted((root / "ideas/donacion").rglob("*.md")):
        meta, body = frontmatter(path.read_text(encoding="utf-8"))
        route = meta.get("permalink", "")
        assert (route.startswith("/donacion/") and route.endswith("/")
                and not any(c in route for c in ("?", "#", "\\"))
                and ".." not in route.split("/") and "//" not in route), path
        assert route not in pages, f"Ruta duplicada: {route}"
        assert meta.get("category") == "Donación" and meta.get("title"), path
        assert meta.get("status") == "published", path
        assert meta.get("published") is True, path
        assert meta.get("visibility") == "public", path
        assert meta.get("editorial_status") == "pending_review" and meta.get("reviewed") is False, path
        record = {"path": path.relative_to(root), "meta": meta, "body": body}
        pages[route] = record
        if meta.get("code"):
            assert meta["code"] not in topics, f"Código duplicado: {meta['code']}"
            topics[meta["code"]] = record
    expected_codes = {f"CF-DON-{code}-{n:03d}" for code, role in ROLES.items()
                      for n in range(1, role["topics"] + 1)}
    assert set(topics) == expected_codes, "Deben existir exactamente las 40 fichas reales de Donación"
    assert len(pages) == 60, "Se requieren 40 fichas y 20 índices"

    expected_routes = {category["url"]}
    for code, spec in ROLES.items():
        role = roles[spec["id"]]
        assert role["name"] == spec["name"] and role.get("section_layout") != "areas", role
        role_url = role["url"]
        assert role_url.startswith(category["url"]) and role_url.endswith("/"), role
        assert pages[role_url]["meta"].get("role") == role["name"], role_url
        expected_routes.add(role_url)
        ordered = [topics[f"CF-DON-{code}-{n:03d}"]["meta"] for n in range(1, spec["topics"] + 1)]
        stage_ids = {f"ORG-DON-{code}-{n:02d}" for n in range(1, spec["stages"] + 1)}
        assert {m.get("stage_id") for m in ordered} == stage_ids, role["name"]
        stage_routes = {m.get("stage_url") for m in ordered}
        assert len(stage_routes) == spec["stages"], role["name"]
        references = []
        for index, meta in enumerate(ordered):
            route, stage_url = meta["permalink"], meta["stage_url"]
            assert meta["role"] == role["name"] and route.startswith(stage_url), meta["code"]
            assert stage_url.startswith(role_url) and stage_url != role_url, meta["code"]
            stage = pages[stage_url]["meta"]
            assert not stage.get("code") and stage.get("stage_id") == meta["stage_id"], meta["code"]
            assert stage.get("role") == role["name"] and stage.get("stage") == meta["stage"], meta["code"]
            refs = meta.get("classification_refs")
            assert isinstance(refs, list), f"{meta['code']}: falta la lista de referencias principales"
            references.extend(refs)
            for direction, offset in (("prev", -1), ("next", 1)):
                neighbor = ordered[index + offset] if 0 <= index + offset < len(ordered) else None
                assert meta.get(direction + "_code") == (neighbor["code"] if neighbor else None), meta["code"]
                assert meta.get(direction + "_title") == (neighbor["title"] if neighbor else None), meta["code"]
                expected_url = neighbor["permalink"] if neighbor else None
                assert meta.get(direction + "_url") == expected_url, meta["code"]
            expected_routes.add(route)
        expected_refs = {f"CL-DON-{code}-{n:03d}" for n in range(1, spec["classification"] + 1)}
        assert set(references) == expected_refs and len(references) == len(expected_refs), (
            f"{role['name']}: las referencias principales deben cubrir {spec['classification']} CL sin duplicados")
        expected_routes.update(stage_routes)
    assert set(pages) == expected_routes, "Índice ausente o fuera de la jerarquía de Donación"
    return config, categories, category, pages, topics


def save_report(name, data):
    artifacts = ROOT / "ui-artifacts"
    artifacts.mkdir(exist_ok=True)
    (artifacts / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify(site: Path, source: Path):
    config, _, category, pages, topics = inventory(source.resolve())
    base = config.get("baseurl", "").rstrip("/")
    origin = config["url"].rstrip("/")
    site = site.resolve()
    built = {"/" + path.parent.relative_to(site).as_posix() + "/"
             for path in (site / "donacion").rglob("index.html")}
    assert built == set(pages), "El render debe contener exactamente las 60 rutas de Donación"
    sharing = json.loads((site / "mantenimiento/share_catalog.json").read_text(encoding="utf-8"))
    items = sharing["items"]
    assert sharing["total_fichas"] == len(items) == 192
    assert len({item["code"] for item in items}) == 192
    assert Counter(item["category"] for item in items) == {"Donación": 40, "Financiamiento Reembolsable": 99, "Recompensa": 53}
    donation = {item["code"]: item for item in items if item["category"] == "Donación"}
    assert set(donation) == set(topics) and all(item["public_searchable"] is True for item in items)
    all_topic_links = {urlsplit(item["canonical_url"]).path for item in items}
    roles = {role["name"]: role for role in category["roles"]}
    role_links = [base + role["url"] for role in category["roles"]]
    documents = {}
    for route, record in pages.items():
        path = site / route.strip("/") / "index.html"
        html = path.read_text(encoding="utf-8")
        assert "{{" not in html and "{%" not in html, f"Liquid sin resolver: {route}"
        page = documents[route] = Document(path).root
        meta = record["meta"]
        role = roles.get(meta.get("role"))
        heading = meta["title"] if meta.get("code") or role is None else (
            role["name"] if route == role["url"] else meta["stage"])
        assert [normalized(n.text) for n in page.all() if n.tag == "h1"] == [heading], route
        assert any(n.tag == "title" and normalized(n.text) == meta["title"] + " · " + config["title"]
                   for n in page.all()), route
        assert any(n.tag == "link" and n.attrs.get("rel") == "canonical"
                   and n.attrs.get("href") == origin + base + route for n in page.all()), route
        assert any(n.tag == "meta" and n.attrs.get("name") == "robots"
                   and "noindex" in n.attrs.get("content", "") for n in page.all()), route
        assert links(page.having_class("fr-role-tabs")[0]) == role_links, route
        crumbs = [base + "/", base + category["url"]]
        if role:
            crumbs.append(base + role["url"])
        if meta.get("code"):
            crumbs.append(base + meta["stage_url"])
        assert links(page.having_class("breadcrumbs")[0]) == crumbs, route
        if role and route != role["url"]:
            stages = {base + t["meta"]["stage_url"] for t in topics.values() if t["meta"]["role"] == role["name"]}
            jumps = links(page.having_class("fr-jump-panel")[0])
            assert len(jumps) == len(stages) and set(jumps) == stages, route
        if meta.get("code"):
            assert page.having_class("canonical-code")[0].text.strip() == meta["code"], route
            notices = page.having_class("test-note")
            assert len(notices) == 1 and "Pendiente de revisión editorial." in notices[0].text, route
            expected = [base + meta[key] for key in ("prev_url", "next_url") if meta.get(key)]
            nav = page.having_class("page-nav")[0]
            assert links(nav) == expected, f"Secuencia incorrecta o cruce de rol: {meta['code']}"
            titles = [normalized(n.text) for n in nav.all() if n.tag == "strong"]
            assert titles == [meta[key] for key in ("prev_title", "next_title") if meta.get(key)], route
            entry = donation[meta["code"]]
            assert (entry["title"], entry["role"], entry["stage"], entry["canonical_url"]) == (
                meta["title"], meta["role"], meta["stage"], origin + base + route), meta["code"]
        elif role and route != role["url"]:
            expected = {base + t["meta"]["permalink"] for t in topics.values() if t["meta"]["stage_url"] == route}
            observed = [href for href in links(page.having_class("fr-stage-content")[0]) if href in all_topic_links]
            assert len(observed) == len(expected) and set(observed) == expected, route
    assert links(documents[category["url"]].having_class("fr-role-grid")[0]) == role_links
    home = Document(site / "index.html").root
    assert all(url in links(home.having_class("home-routes")[0]) for url in role_links)
    for code, spec in ROLES.items():
        role = roles[spec["name"]]
        hub = documents[role["url"]]
        topic_nodes = [n for n in hub.all() if "data-fr-topic" in n.attrs]
        expected = [f"CF-DON-{code}-{n:03d}" for n in range(1, spec["topics"] + 1)]
        assert [n.attrs["data-fr-code"] for n in topic_nodes] == expected, role["name"]
        assert [n.attrs["href"] for n in topic_nodes] == [base + topics[c]["meta"]["permalink"] for c in expected]
        assert len(hub.having_class("fr-section")) == spec["stages"]
        assert hub.having_class("fr-hub")[0].attrs["data-section-layout"] == "stages"
        assert len(hub.having_class("fr-review-label")) == spec["topics"]
    control = json.loads((site / "mantenimiento/control_catalog.json").read_text(encoding="utf-8"))
    assert {item["code"] for item in control["items"]} == {item["code"] for item in items}
    routes = audit_routes(site, config, control)
    integrity = audit_integrity(site, root=source.resolve())
    save_report("donation-navigation.json", {"scope": "rendered_public_site", "donation_routes": len(built),
                "donation_topics": len(topics), "catalog_topics": len(items), "routes": routes, "integrity": integrity})
    assert routes["checked"] == routes["reachable"] == 192 and not routes["missing_routes"] and not routes["unreachable_topics"], routes
    assert routes["unique_codes"] and routes["unique_routes"], routes
    assert integrity["pages"] and not integrity["errors"], integrity
    print("PASS: 60 rutas Donación; títulos, roles, etapas y secuencia; catálogo 192 = 40 Donación + 99 FR + 53 Recompensa; enlaces íntegros")


def smoke(site: Path, source: Path):
    import os
    from functools import partial
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread
    from playwright.sync_api import sync_playwright, expect

    config, _, category, _, topics = inventory(source.resolve())
    base = config.get("baseurl", "").rstrip("/")
    origin = config["url"].rstrip("/")
    roles = {role["id"]: role for role in category["roles"]}
    artifacts = ROOT / "ui-artifacts"
    artifacts.mkdir(exist_ok=True)

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if base and (self.path == base or self.path.startswith(base + "/")):
                self.path = self.path[len(base):] or "/"
            super().do_GET()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(site.resolve())))
    Thread(target=server.serve_forever, daemon=True).start()
    local = f"http://127.0.0.1:{server.server_port}"

    def local_only(route):
        request = urlsplit(route.request.url)
        if request.netloc != urlsplit(origin).netloc:
            return route.abort()
        response = route.fetch(url=local + request.path + ("?" + request.query if request.query else ""))
        route.fulfill(response=response)

    def fits(page):
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), page.url

    passed = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=os.environ.get("CHROMIUM_EXECUTABLE_PATH"))
            for width in (1280, 390):
                context = browser.new_context(viewport={"width": width, "height": 900}, reduced_motion="reduce")
                context.route("**/*", local_only)
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                for code, spec in ROLES.items():
                    role = roles[spec["id"]]
                    first = topics[f"CF-DON-{code}-001"]["meta"]
                    second = topics[f"CF-DON-{code}-002"]["meta"]
                    last = topics[f"CF-DON-{code}-{spec['topics']:03d}"]["meta"]
                    page.goto(origin + base + category["url"])
                    page.locator(f'.fr-role-card[href="{base + role["url"]}"]').click()
                    expect(page.locator("h1")).to_have_text(role["name"])
                    expect(page.locator("[data-fr-topic]")).to_have_count(spec["topics"])
                    expect(page.locator("[data-fr-filter]")).to_be_visible()
                    assert page.locator("[data-fr-filter-section] option").count() == spec["stages"] + 1
                    sections = page.locator(".fr-section")
                    page.locator("[data-fr-filter-section]").select_option(sections.last.get_attribute("id"))
                    expect(page.locator(".fr-section:visible")).to_have_count(1)
                    page.locator("[data-fr-filter-query]").fill(last["code"])
                    expect(page.locator("[data-fr-topic]:visible")).to_have_count(1)
                    expect(page.locator("[data-fr-topic]:visible")).to_have_attribute("data-fr-code", last["code"])
                    fits(page)
                    page.screenshot(path=str(artifacts / f'donation-{role["id"]}-{width}.png'), full_page=True)
                    page.locator("[data-fr-filter-clear]").click()
                    page.locator("[data-fr-filter-query]").fill(first["code"])
                    page.locator("[data-fr-topic]:visible").click()
                    expect(page).to_have_url(origin + base + first["permalink"])
                    page.locator(".page-nav-next").click()
                    expect(page).to_have_url(origin + base + second["permalink"])
                    page.locator(".page-nav-item:not(.page-nav-next)").click()
                    expect(page).to_have_url(origin + base + first["permalink"])
                    fits(page)
                    page.locator(".fr-jump > summary").click()
                    page.locator(f'.fr-jump-panel a[href="{base + last["stage_url"]}"]').click()
                    expect(page.locator(".fr-stage-content")).to_be_visible()
                    page.locator(f'.fr-stage-content a[href="{base + last["permalink"]}"]').click()
                    expect(page.locator("h1")).to_have_text(last["title"])
                    expect(page.locator(".page-nav-next")).to_have_count(0)
                    fits(page)
                    page.goto(origin + base + "/#buscar")
                    expect(page.locator("#public-search-query")).to_be_enabled()
                    page.locator("#public-search-query").fill("Donación")
                    page.locator("#public-search-filter-toggle").click()
                    page.locator("#public-search-category").select_option("Donación")
                    page.locator("#public-search-role").select_option(role["name"])
                    expect(page.locator("#public-search-count")).to_have_text(f'Mostrando 6 de {spec["topics"]} resultados')
                    assert page.locator("#public-search-stage option").count() == spec["stages"] + 1
                    page.locator("#public-search-stage").select_option(first["stage"])
                    page.locator("#public-search-query").fill(first["code"])
                    expect(page.locator(".public-search-result")).to_have_count(1)
                    expect(page.locator(".public-search-result")).to_have_attribute("href", origin + base + first["permalink"])
                    page.locator(".public-search-result").click()
                    expect(page.locator("h1")).to_have_text(first["title"])
                    fits(page)
                    passed.append(f'{width}px / {role["name"]}: recorrido, etapa, filtros, buscador y anterior/siguiente')
                first = topics["CF-DON-DON-001"]["meta"]
                page.goto(origin + base + "/#orientacion")
                page.locator("#guidance-start").click()
                page.locator(".guidance-choice").filter(has_text="Apoyar o invertir en una iniciativa").click()
                page.get_by_role("button", name="Donación Aportes sin obligación de devolución", exact=True).click()
                page.get_by_role("button", name="Donantes", exact=True).click()
                page.get_by_role("button", name=first["stage"], exact=True).click()
                page.get_by_role("button", name=first["title"], exact=True).click()
                expect(page.locator(".guidance-context")).to_have_text("Donación · Donantes · " + first["stage"])
                expect(page.locator(".guidance-canonical-link")).to_have_attribute("href", origin + base + first["permalink"])
                page.locator(".guidance-canonical-link").click()
                expect(page.locator("h1")).to_have_text(first["title"])
                fits(page)
                passed.append(f"{width}px: orientación Donación → Donantes → etapa → ficha canónica")
                assert not errors, errors
                context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    save_report("donation-browser.json", {"scope": "rendered_public_site", "passed": passed})
    print("\n".join("PASS: " + case for case in passed))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "smoke"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("--source", type=Path, default=SOURCE, help="Raíz de las fuentes públicas que produjo el sitio")
    args = parser.parse_args()
    {"verify": verify, "smoke": smoke}[args.command](args.directory, args.source)


if __name__ == "__main__":
    main()
