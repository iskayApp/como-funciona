"""CF-UX-001: real catalog filters, resources, reading, clipboard and responsive layout."""
import json
import os
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright, expect
from smoke_fr_navigation import SITE, BASE, ARTIFACTS, Handler, fits


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(SITE)))
    Thread(target=server.serve_forever, daemon=True).start()
    home = f'http://127.0.0.1:{server.server_port}{BASE}/'
    topic = 'financiamiento-reembolsable/promotores/prepara-la-revision-profesional/que-colaboradores-necesitas-segun-el-monto-solicitado/'
    passed = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE_PATH'))
            for width in (1280, 768, 390, 320):
                context = browser.new_context(viewport={'width': width, 'height': 900}, reduced_motion='reduce', permissions=['clipboard-read', 'clipboard-write'])
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(home)
                expect(page.locator('#public-search-query')).to_be_enabled()
                assert page.locator('.resource-card').count() == 2
                assert page.locator('.featured-card').count() == 3
                page.locator('.resource-card').last.scroll_into_view_if_needed()
                page.wait_for_function('Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)')
                fits(page)
                page.evaluate('window.scrollTo(0,0)')
                page.screenshot(path=str(ARTIFACTS / f'design-home-{width}.png'), full_page=True)
                page.locator('#public-search-query').fill('colaboradores')
                page.locator('#public-search-filter-toggle').click()
                page.locator('#public-search-category').select_option('Financiamiento Reembolsable')
                page.locator('#public-search-role').select_option('Promotores')
                page.locator('#public-search-query').fill('')
                page.locator('#public-search-stage').select_option('Prepara la revisión profesional')
                page.locator('#public-search-type').select_option('diagram')
                expect(page.locator('.public-search-result')).to_have_count(1)
                assert topic in page.locator('.public-search-result').get_attribute('href')
                fits(page)
                page.locator('#public-search-role').select_option('Inversores')
                assert page.locator('#public-search-stage').input_value() == ''
                assert page.locator('#public-search-type').input_value() == ''
                assert page.locator('#public-search-type option[value="diagram"]').count() == 0
                page.locator('#public-search-clear').click()
                for id_ in ('query', 'category', 'role', 'stage', 'type'):
                    assert page.locator('#public-search-' + id_).input_value() == ''
                expect(page.locator('.public-search-result')).to_have_count(0)
                resource_links = page.locator('.resource-card').evaluate_all('(links) => links.map(a => a.href)')
                for link in resource_links:
                    page.goto(link)
                    anchor = link.split('#')[1]
                    assert page.locator('[id="' + anchor + '"]').count() == 1
                    fits(page)
                page.goto(home + 'financiamiento-reembolsable/promotores/')
                sidebar = page.locator('.hub-index details')
                if not sidebar.get_attribute('open') and not sidebar.evaluate('(node) => node.open'):
                    sidebar.locator('summary').click()
                page.locator('[data-hub-target="seccion-3"]').click()
                assert page.locator('#seccion-3').evaluate('(node) => node.open')
                assert page.locator('#seccion-3 [data-fr-topic]').count() == 6
                fits(page)
                page.evaluate('document.activeElement.blur(); window.scrollTo(0,0)')
                page.screenshot(path=str(ARTIFACTS / f'design-promotores-{width}.png'), full_page=True)
                page.goto(home + topic)
                expect(page.locator('.answer-summary')).to_be_visible()
                assert page.locator('.topic-index nav a').count() >= 6
                toc = page.locator('.topic-index details')
                if not toc.evaluate('(node) => node.open'):
                    toc.locator('summary').click()
                toc.locator('nav a').first.click()
                assert page.url.endswith('#respuesta-breve')
                assert page.locator('.table-scroll table tr').count() == 5
                assert page.locator('.table-scroll table th').count() == 3
                assert 'USD 470.000,00' in page.locator('.table-scroll').inner_text()
                page.locator('.copy-link-button').first.click()
                expect(page.locator('#copy-feedback')).to_contain_text('copiado')
                assert page.evaluate('navigator.clipboard.readText()') == page.locator('#share-ficha').get_attribute('href')
                fits(page)
                page.evaluate('window.scrollTo(0,0)')
                page.screenshot(path=str(ARTIFACTS / f'design-ficha-{width}.png'), full_page=True)
                assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
                assert not errors, errors
                context.close()
                passed.append(f'{width}px: filters and dependent resets, media anchors, role sidebar, complete canonical table, clipboard, no storage, no JS errors')
            context = browser.new_context(viewport={'width':320, 'height':900})
            context.route('**/mantenimiento/share_catalog.json', lambda route: route.fulfill(status=503, body='Unavailable'))
            page = context.new_page()
            page.goto(home)
            expect(page.locator('#public-search-count')).to_contain_text('no está disponible')
            assert page.locator('.resource-card').count() == 2
            assert page.locator('.fr-role-card').count() == 12
            assert page.locator(f'.fr-role-card[href^="{BASE}/financiamiento-reembolsable/"]').count() == 3
            assert page.locator(f'.fr-role-card[href^="{BASE}/donacion/"]').count() == 3
            assert page.locator(f'.fr-role-card[href^="{BASE}/recompensa/"]').count() == 3
            assert page.locator(f'.fr-role-card[href^="{BASE}/precompra/"]').count() == 3
            fits(page)
            context.close()
            passed.append('Catalog failure: static resources and twelve role routes across four published categories remain available')
            context = browser.new_context(java_script_enabled=False, viewport={'width':320,'height':900})
            page = context.new_page()
            page.goto(home)
            assert page.locator('.fr-role-card').count() == 12
            assert page.locator(f'.fr-role-card[href^="{BASE}/financiamiento-reembolsable/"]').count() == 3
            assert page.locator(f'.fr-role-card[href^="{BASE}/donacion/"]').count() == 3
            assert page.locator(f'.fr-role-card[href^="{BASE}/recompensa/"]').count() == 3
            assert page.locator(f'.fr-role-card[href^="{BASE}/precompra/"]').count() == 3
            fits(page)
            page.goto(home + topic)
            assert page.locator('table th').count() == 3
            assert page.locator('#media-fr-pro-13-colaboradores-monto').count() == 1
            fits(page)
            context.close()
            passed.append('No JavaScript: full canonical explanation, table and original diagram remain usable')
            browser.close()
    finally:
        server.shutdown()
    (ARTIFACTS / 'visual-refresh-report.json').write_text(json.dumps({'passed':passed}, ensure_ascii=False, indent=2))
    print('\n'.join('PASS: ' + line for line in passed))


if __name__ == '__main__':
    main()
