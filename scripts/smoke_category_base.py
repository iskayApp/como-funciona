"""Exercise generic navigation and maintenance using the actual Jekyll output.
The technical report is a controlled fixture, not a live TikTok/API check.
"""
import os
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
import json
import re
import yaml
from playwright.sync_api import sync_playwright
from build_maintenance_control import is_public
from smoke_fr_navigation import ROOT, SITE, BASE, ARTIFACTS, Handler, fits

PUBLIC_ROLES = {
    'financiamiento-reembolsable': [('promotores',33,6),('inversores',37,7),('colaboradores',29,8)],
    'donacion': [('promotores',18,7),('donantes',14,5),('colaboradores',8,4)],
}


def report_fixture():
    items = []
    config = yaml.safe_load((ROOT / '_config.yml').read_text())
    for source in sorted((ROOT / 'ideas').rglob('*.md')):
        raw = source.read_text()
        if not raw.startswith('---\n'):
            continue
        meta = yaml.safe_load(raw.split('---\n', 2)[1]) or {}
        if not meta.get('code') or not is_public(meta, source.relative_to(ROOT).as_posix(), config):
            continue
        order = re.search(r'/(\d+)-', meta.get('stage_url', ''))
        items.append({'code':meta['code'], 'title':meta['title'], 'canonical_url':meta['permalink'],
                      'category':meta.get('category'), 'role':meta.get('role'),
                      'stage':meta.get('stage'), 'stage_url':meta.get('stage_url'),
                      'stage_order':int(order[1]) if order else 999,
                      'content_version':meta.get('content_version'), 'reviewed':str(meta.get('reviewed') or ''),
                      'status':'SIN COMPROBAR', 'media':[], 'checks':[]})
    return {'generated_at':'2026-11-04T00:00:00Z', 'summary':{'fichas':len(items)}, 'items':items,
            'services':{'tiktok':{'status':'SIN COMPROBAR','detail':'Fixture de prueba; no consulta externa.'}},
            'tiktok_inventory':{'videos':[]}}


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(SITE)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    home = origin + BASE + '/'
    fixture = report_fixture()
    assert len(fixture['items']) == 139
    assert sum(i['category'] == 'Financiamiento Reembolsable' for i in fixture['items']) == 99
    assert sum(i['category'] == 'Donación' for i in fixture['items']) == 40
    tested = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=os.environ.get("CHROMIUM_EXECUTABLE_PATH"))
            for width in (1280, 390, 320):
                context = browser.new_context(viewport={'width':width,'height':900})
                context.route('**/mantenimiento/status.json', lambda route: route.fulfill(json=fixture))
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(home)
                assert page.locator('.category-card').count() == 5
                assert page.locator('.category-card[data-availability="available"]').count() == 2
                assert page.locator('.category-card[data-category="financiamiento-reembolsable"]').get_attribute('data-availability') == 'available'
                assert page.locator('.category-card[data-category="donacion"]').get_attribute('data-availability') == 'available'
                assert page.locator('.category-card-pending a').count() == 0
                assert page.locator('.category-role-link').count() == 6
                assert page.evaluate('(document.querySelector("#buscar").compareDocumentPosition(document.querySelector("#categorias")) & 4) !== 0')
                assert page.evaluate('(document.querySelector("#orientacion").compareDocumentPosition(document.querySelector("#categorias")) & 4) !== 0')
                assert page.locator('h1').inner_text() == 'Aprende a usar iskay.app'
                assert 'Financiamiento Reembolsable' not in page.title()
                fits(page)
                page.locator('.fr-menu > summary').click()
                assert page.locator('[data-menu-category]').count() == 5
                assert page.locator('.category-menu-pending a').count() == 0
                fits(page)
                page.keyboard.press('Escape')
                page.screenshot(path=str(ARTIFACTS / f'category-home-{width}.png'), full_page=True)
                page.goto(home + 'mantenimiento/')
                assert page.locator('[data-maint-category]').count() == 5
                assert page.locator('[data-maint-role]').count() == 6
                assert page.locator('[data-maint-topic]').count() == 139
                for category, roles in PUBLIC_ROLES.items():
                    category_group = page.locator(f'[data-maint-category="{category}"]')
                    assert category_group.locator('[data-maint-topic]').count() == sum(r[1] for r in roles)
                    for role, count, sections in roles:
                        group = category_group.locator(f'[data-maint-role="{role}"]')
                        assert group.locator('[data-maint-topic]').count() == count
                        assert group.locator('[data-maint-section]').count() == sections
                page.locator('[data-maint-view-link="m-publicacion"]').click()
                page.wait_for_selector('[data-technical-section]', state='attached')
                page.locator('[data-technical-section]').evaluate_all('(nodes)=>nodes.forEach(node=>node.open=true)')
                page.wait_for_function('document.querySelectorAll("[data-technical-topic]").length === 139')
                assert page.locator('[data-technical-category]').count() == 2
                assert page.locator('[data-technical-role]').count() == 6
                assert page.locator('[data-technical-section]').count() == 37
                for category, roles in PUBLIC_ROLES.items():
                    group = page.locator(f'[data-technical-category="{category}"]')
                    assert group.locator('[data-technical-topic]').count() == sum(r[1] for r in roles)
                    assert group.locator('[data-technical-section]').count() == sum(r[2] for r in roles)
                assert page.locator('.maint-ficha-actions a').first.get_attribute('href').startswith(home)
                page.locator('[data-maint-view-link="m-contenido"]').click()
                collaborators = page.locator('[data-maint-category="donacion"] [data-maint-role="colaboradores"]')
                collaborators.locator(':scope > summary').click()
                collaborators.locator('[data-maint-section] > summary').first.click()
                assert collaborators.locator('[data-maint-topic]').first.is_visible()
                fits(page)
                page.screenshot(path=str(ARTIFACTS / f'category-maintenance-{width}.png'))
                assert not errors, errors
                tested.append(f'{width}px: five categories, two available, six roles, 139 topics (99 FR + 40 DON), 37 isolated sections')
                context.close()
            context = browser.new_context(java_script_enabled=False, viewport={'width':320,'height':900})
            page = context.new_page()
            page.goto(home)
            assert page.locator('.category-role-link').count() == 6
            page.locator(f'.category-role-link[href="{BASE}/donacion/colaboradores/"]').click()
            assert '/donacion/colaboradores/' in page.url
            for category in PUBLIC_ROLES:
                page.goto(home + 'mantenimiento/')
                group = page.locator(f'[data-maint-category="{category}"] [data-maint-role="promotores"]')
                group.locator(':scope > summary').click()
                group.locator('[data-maint-section] > summary').first.click()
                group.locator('[data-maint-topic]').first.click()
                assert f'/{category}/promotores/' in page.url
                fits(page)
            tested.append('No JavaScript: category -> role and maintenance -> section -> canonical topic')
            context.close()
            context = browser.new_context()
            context.route('**/mantenimiento/status.json', lambda route: route.fulfill(status=503,body='Unavailable'))
            page = context.new_page()
            page.goto(home + 'mantenimiento/')
            page.wait_for_function('document.querySelector("#maintenance-dashboard").textContent.includes("No se pudo cargar")')
            assert page.locator('[data-maint-topic]').count() == 139
            tested.append('Technical report failure does not remove native hierarchy')
            context.close()
            browser.close()
    finally:
        server.shutdown()
    (ARTIFACTS / 'category-base-report.json').write_text(json.dumps({'passed':tested}, ensure_ascii=False, indent=2))
    print('\n'.join('PASS: ' + line for line in tested))


if __name__ == '__main__':
    main()
