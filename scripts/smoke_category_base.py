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
from smoke_fr_navigation import ROOT, SITE, BASE, ARTIFACTS, Handler, fits


def report_fixture():
    items = []
    for source in sorted((ROOT / 'ideas/financiamiento-reembolsable').rglob('*.md')):
        raw = source.read_text()
        if not raw.startswith('---\n'):
            continue
        meta = yaml.safe_load(raw.split('---\n', 2)[1]) or {}
        if not meta.get('code'):
            continue
        order = re.search(r'/(\d+)-', meta.get('stage_url', ''))
        items.append({'code':meta['code'], 'title':meta['title'], 'canonical_url':meta['permalink'],
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
    assert len(fixture['items']) == 99
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
                assert page.locator('.category-card[data-availability="available"]').count() == 1
                assert page.locator('.category-card-pending a').count() == 0
                assert page.locator('.category-role-link').count() == 3
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
                assert page.locator('[data-maint-role]').count() == 3
                assert page.locator('[data-maint-topic]').count() == 99
                for role, count, sections in [('promotores',33,6),('inversores',37,7),('colaboradores',29,8)]:
                    group = page.locator(f'[data-maint-role="{role}"]')
                    assert group.locator('[data-maint-topic]').count() == count
                    assert group.locator('[data-maint-section]').count() == sections
                page.wait_for_selector('[data-technical-topic]', state='attached')
                assert page.locator('[data-technical-topic]').count() == 99
                assert page.locator('[data-technical-category]').count() == 1
                assert page.locator('[data-technical-role]').count() == 3
                assert page.locator('[data-technical-section]').count() == 21
                page.locator('[data-maint-role="colaboradores"] > summary').click()
                page.locator('[data-maint-role="colaboradores"] [data-maint-section] > summary').first.click()
                assert page.locator('[data-maint-role="colaboradores"] [data-maint-topic]').first.is_visible()
                fits(page)
                page.screenshot(path=str(ARTIFACTS / f'category-maintenance-{width}.png'))
                assert not errors, errors
                tested.append(f'{width}px: home, five categories, three roles, 99 topics, 21 isolated sections, technical fixture')
                context.close()
            context = browser.new_context(java_script_enabled=False, viewport={'width':320,'height':900})
            page = context.new_page()
            page.goto(home)
            assert page.locator('.category-role-link').count() == 3
            page.locator('.category-role-link').last.click()
            assert 'colaboradores' in page.url
            page.goto(home + 'mantenimiento/')
            page.locator('[data-maint-role="promotores"] > summary').click()
            page.locator('[data-maint-role="promotores"] [data-maint-section] > summary').first.click()
            page.locator('[data-maint-role="promotores"] [data-maint-topic]').first.click()
            assert '/financiamiento-reembolsable/promotores/' in page.url
            fits(page)
            tested.append('No JavaScript: category -> role and maintenance -> section -> canonical topic')
            context.close()
            context = browser.new_context()
            context.route('**/mantenimiento/status.json', lambda route: route.fulfill(status=503,body='Unavailable'))
            page = context.new_page()
            page.goto(home + 'mantenimiento/')
            page.wait_for_function('document.querySelector("#maintenance-dashboard").textContent.includes("No se pudo cargar")')
            assert page.locator('[data-maint-topic]').count() == 99
            tested.append('Technical report failure does not remove native hierarchy')
            context.close()
            browser.close()
    finally:
        server.shutdown()
    (ARTIFACTS / 'category-base-report.json').write_text(json.dumps({'passed':tested}, ensure_ascii=False, indent=2))
    print('\n'.join('PASS: ' + line for line in tested))


if __name__ == '__main__':
    main()
