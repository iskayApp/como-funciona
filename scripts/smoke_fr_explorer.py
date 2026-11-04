"""Exercise role-local filters against the real Jekyll build and canonical links."""
import os
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
import json
import unicodedata
from playwright.sync_api import sync_playwright
from smoke_fr_navigation import Handler, SITE, BASE, FR, ROLES, ARTIFACTS, fits


def fold(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if not unicodedata.combining(c)).lower()


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(SITE)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    passed = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_EXECUTABLE_PATH"))
            for width in (1280, 390, 320):
                context = browser.new_context(viewport={'width': width, 'height': 900})
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                for slug, role, total, count in ROLES:
                    page.goto(origin + BASE + FR + slug + '/')
                    controls = page.locator('[data-fr-filter]')
                    query = page.locator('[data-fr-filter-query]')
                    select = page.locator('[data-fr-filter-section]')
                    clear = page.locator('[data-fr-filter-clear]')
                    sections = page.locator('.fr-section')
                    links = page.locator('[data-fr-topic]')
                    visible = page.locator('[data-fr-topic]:visible')
                    assert controls.is_visible()
                    assert links.count() == total
                    assert select.locator('option').count() == count + 1
                    snapshot = links.evaluate_all('(nodes) => nodes.map(n => [n.href, n.dataset.frCode, n.parentElement.textContent])')
                    assert len({row[1] for row in snapshot}) == total
                    sections.first.locator('summary').click()
                    original_open = sections.evaluate_all('(nodes) => nodes.map(n => n.open)')
                    query.fill(snapshot[0][1])
                    assert visible.count() == 1
                    assert visible.first.get_attribute('data-fr-code') == snapshot[0][1]
                    assert page.locator('[data-fr-filter-status]').inner_text().startswith(f'1 de {total}')
                    fits(page)
                    clear.click()
                    assert sections.evaluate_all('(nodes) => nodes.map(n => n.open)') == original_open
                    assert query.evaluate('(node) => node === document.activeElement')
                    title = links.first.locator('span').first.inner_text()
                    query.fill(fold(title))
                    assert visible.count() >= 1
                    assert snapshot[0][1] in visible.evaluate_all('(nodes) => nodes.map(n => n.dataset.frCode)')
                    clear.click()
                    last = sections.last
                    select.select_option(last.get_attribute('id'))
                    assert page.locator('.fr-section:visible').count() == 1
                    assert visible.count() == last.locator('[data-fr-topic]').count()
                    if slug == 'colaboradores':
                        assert select.locator('optgroup').count() == 2
                        assert select.locator('optgroup[label="Base común"] option').count() == 4
                        assert select.locator('optgroup[label="Áreas de colaboración"] option').count() == 4
                        assert not page.locator('[data-fr-group-heading="common"]').is_visible()
                        assert page.locator('[data-fr-group-heading="area"]').is_visible()
                    fits(page)
                    query.fill(snapshot[0][1])
                    assert visible.count() == 0
                    assert page.locator('[data-fr-filter-empty]').is_visible()
                    clear.click()
                    query.fill('<img src=x onerror=alert(1)>')
                    assert visible.count() == 0
                    assert controls.locator('img').count() == 0
                    query.press('Enter')
                    assert page.url.endswith('/' + slug + '/')
                    clear.click()
                    query.focus()
                    page.keyboard.press('Tab')
                    assert select.evaluate('(node) => node === document.activeElement')
                    select.select_option(sections.first.get_attribute('id'))
                    assert page.locator('.fr-section:visible').count() == 1
                    fits(page)
                    page.screenshot(path=str(ARTIFACTS / f'explorar-{slug}-{width}.png'), full_page=True)
                    clear.click()
                    assert links.evaluate_all('(nodes) => nodes.map(n => [n.href, n.dataset.frCode, n.parentElement.textContent])') == snapshot
                    assert page.locator('.fr-section:visible').count() == count
                    assert clear.is_disabled()
                    assert page.evaluate('localStorage.length === 0 && sessionStorage.length === 0')
                    assert not errors, errors
                    passed.append(f'{width}px / {role}: code, accents, section, combination, reset, keyboard, no results, no storage')
                context.close()
            context = browser.new_context(java_script_enabled=False, viewport={'width': 320, 'height': 900})
            page = context.new_page()
            for slug, role, total, count in ROLES:
                page.goto(origin + BASE + FR + slug + '/')
                assert not page.locator('[data-fr-filter]').is_visible()
                assert page.locator('[data-fr-topic]').count() == total
                page.locator('.fr-section > summary').first.click()
                assert page.locator('[data-fr-topic]').first.is_visible()
                fits(page)
            context.close()
            browser.close()
            passed.append('Without JavaScript: all 99 canonical links remain available through native disclosures')
    finally:
        server.shutdown()
        server.server_close()
    (ARTIFACTS / 'explorer-report.json').write_text(json.dumps({'passed': passed}, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\n'.join('PASS: ' + case for case in passed))


if __name__ == '__main__':
    main()
