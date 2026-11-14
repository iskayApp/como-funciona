"""Exercise generic navigation and maintenance using the actual Jekyll output.
The technical report is a controlled fixture, not a live TikTok/API check.
"""
import os
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlsplit
import json
import re
import yaml
from playwright.sync_api import sync_playwright, expect
from build_maintenance_control import is_public
from smoke_fr_navigation import ROOT, SITE, BASE, ARTIFACTS, Handler, fits

PUBLIC_ROLES = {
    'financiamiento-reembolsable': [('promotores',33,6),('inversores',37,7),('colaboradores',29,8)],
    'donacion': [('promotores',18,7),('donantes',14,5),('colaboradores',8,4)],
    'recompensa': [('promotores',30,9),('contribuyentes',14,5),('colaboradores',9,4)],
    'precompra': [('promotores',36,9),('precompradores',21,6),('colaboradores',9,4)],
}
EXPECTED_TOPICS = sum(count for roles in PUBLIC_ROLES.values() for _, count, _ in roles)
EXPECTED_ROLES = sum(len(roles) for roles in PUBLIC_ROLES.values())
EXPECTED_SECTIONS = sum(sections for roles in PUBLIC_ROLES.values() for _, _, sections in roles)


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


def check_precompra_precompradores(browser, local_origin, fixture):
    """Recorre el nuevo rol público con URLs canónicas servidas desde _site."""
    config = yaml.safe_load((ROOT / '_config.yml').read_text())
    public_origin = config['url'].rstrip('/')
    home = public_origin + BASE + '/'
    first = next(item for item in fixture['items'] if item['code'] == 'CF-PRE-PRC-001')
    last = next(item for item in fixture['items'] if item['code'] == 'CF-PRE-PRC-021')
    first_url = public_origin + BASE + first['canonical_url']
    last_url = public_origin + BASE + last['canonical_url']

    def local_only(route):
        requested = urlsplit(route.request.url)
        if requested.netloc != urlsplit(public_origin).netloc:
            return route.abort()
        target = local_origin + requested.path + ('?' + requested.query if requested.query else '')
        route.fulfill(response=route.fetch(url=target))

    context = browser.new_context(viewport={'width':390, 'height':900}, reduced_motion='reduce')
    context.route('**/*', local_only)
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    try:
        page.goto(home)
        page.locator('.category-card[data-category="precompra"] h3 a').click()
        role = page.locator(f'.fr-role-grid .fr-role-card[href="{BASE}/precompra/precompradores/"]')
        expect(role.locator('.fr-card-meta')).to_have_text('21 fichas · 6 etapas')
        role.click()
        expect(page.locator('h1')).to_have_text('Precompradores')
        expect(page.locator('[data-fr-topic]')).to_have_count(21)
        expect(page.locator('.fr-section')).to_have_count(6)
        section = page.locator('.fr-section').first
        if not section.evaluate('(node) => node.open'):
            section.locator(':scope > summary').click()
        section.locator('[data-fr-code="CF-PRE-PRC-001"]').click()
        expect(page).to_have_url(first_url)
        expect(page.locator('h1')).to_have_text(first['title'])
        expect(page.locator('.test-note')).to_contain_text('Pendiente de revisión editorial.')
        fits(page)

        page.goto(home + '#orientacion')
        page.locator('#guidance-start').click()
        choices = page.locator('#guidance-options')
        choices.locator('.guidance-choice').filter(has_text='Explorar las explicaciones disponibles').click()
        choices.get_by_role('button', name='Precompra', exact=True).click()
        choices.get_by_role('button', name='Precompradores', exact=True).click()
        choices.get_by_role('button', name=first['stage'], exact=True).click()
        choices.get_by_role('button', name=first['title'], exact=True).click()
        expect(page.locator('.guidance-context')).to_have_text('Precompra · Precompradores · ' + first['stage'])
        expect(page.locator('.guidance-canonical-link')).to_have_attribute('href', first_url)
        page.locator('.guidance-canonical-link').click()
        expect(page).to_have_url(first_url)
        expect(page.locator('h1')).to_have_text(first['title'])

        page.goto(home + '#buscar')
        expect(page.locator('#public-search-query')).to_be_enabled()
        page.locator('#public-search-query').fill(last['code'])
        result = page.locator('.public-search-result')
        expect(result).to_have_count(1)
        expect(result).to_have_attribute('href', last_url)
        expect(result.locator('.public-search-result-context')).to_contain_text('Precompradores')
        result.click()
        expect(page).to_have_url(last_url)
        expect(page.locator('h1')).to_have_text(last['title'])
        expect(page.locator('.test-note')).to_contain_text('Pendiente de revisión editorial.')
        fits(page)
        assert not errors, errors
    finally:
        context.close()


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(SITE)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    home = origin + BASE + '/'
    fixture = report_fixture()
    assert len(fixture['items']) == EXPECTED_TOPICS == 258
    assert sum(i['category'] == 'Financiamiento Reembolsable' for i in fixture['items']) == 99
    assert sum(i['category'] == 'Donación' for i in fixture['items']) == 40
    assert sum(i['category'] == 'Recompensa' for i in fixture['items']) == 53
    assert sum(i['category'] == 'Precompra' for i in fixture['items']) == 66
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
                assert page.locator('.category-card[data-availability="available"]').count() == len(PUBLIC_ROLES)
                assert page.locator('.category-card[data-category="financiamiento-reembolsable"]').get_attribute('data-availability') == 'available'
                assert page.locator('.category-card[data-category="donacion"]').get_attribute('data-availability') == 'available'
                assert page.locator('.category-card[data-category="recompensa"]').get_attribute('data-availability') == 'available'
                assert page.locator('.category-card[data-category="precompra"]').get_attribute('data-availability') == 'available'
                assert page.locator('.category-card-pending a').count() == 0
                assert page.locator('.category-role-link').count() == EXPECTED_ROLES
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
                assert page.locator('[data-maint-role]').count() == EXPECTED_ROLES
                assert page.locator('[data-maint-topic]').count() == EXPECTED_TOPICS
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
                page.wait_for_function(f'document.querySelectorAll("[data-technical-topic]").length === {EXPECTED_TOPICS}')
                assert page.locator('[data-technical-category]').count() == len(PUBLIC_ROLES)
                assert page.locator('[data-technical-role]').count() == EXPECTED_ROLES
                assert page.locator('[data-technical-section]').count() == EXPECTED_SECTIONS
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
                tested.append(f'{width}px: five categories, {len(PUBLIC_ROLES)} available, {EXPECTED_ROLES} roles, {EXPECTED_TOPICS} topics (99 FR + 40 DON + 53 REC + 66 PRE), {EXPECTED_SECTIONS} isolated sections')
                context.close()
            check_precompra_precompradores(browser, origin, fixture)
            tested.append('390px: Precompra -> Precompradores; 21 fichas, 6 etapas, aviso editorial, orientación y búsqueda canónica de CF-PRE-PRC-021')
            context = browser.new_context(java_script_enabled=False, viewport={'width':320,'height':900})
            page = context.new_page()
            page.goto(home)
            assert page.locator('.category-role-link').count() == EXPECTED_ROLES
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
            assert page.locator('[data-maint-topic]').count() == EXPECTED_TOPICS
            tested.append('Technical report failure does not remove native hierarchy')
            context.close()
            browser.close()
    finally:
        server.shutdown()
    (ARTIFACTS / 'category-base-report.json').write_text(json.dumps({'passed':tested}, ensure_ascii=False, indent=2))
    print('\n'.join('PASS: ' + line for line in tested))


if __name__ == '__main__':
    main()
