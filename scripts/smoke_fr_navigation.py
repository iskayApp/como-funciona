"""Browser checks against the built site: desktop, mobile, keyboard and no JavaScript."""
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import json
import sys
import yaml
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / '_site').resolve()
ARTIFACTS = ROOT / 'ui-artifacts'
ARTIFACTS.mkdir(exist_ok=True)
BASE = yaml.safe_load((ROOT / '_config.yml').read_text()).get('baseurl', '').rstrip('/')
FR = '/financiamiento-reembolsable/'
ROLES = [('promotores', 'Promotores', 33, 6), ('inversores', 'Inversores', 37, 7), ('colaboradores', 'Colaboradores', 29, 8)]


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if BASE and (self.path == BASE or self.path.startswith(BASE + '/')):
            self.path = self.path[len(BASE):] or '/'
        super().do_GET()

    def log_message(self, *args):
        pass


def fits(page):
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'), page.url


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(SITE)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    home = origin + BASE + '/'
    tested = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=os.environ.get("CHROMIUM_EXECUTABLE_PATH"))
            for width in (1280, 390, 320):
                context = browser.new_context(viewport={'width': width, 'height': 900})
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(home)
                assert page.locator('.fr-role-card').count() == 3
                fits(page)
                menu = page.locator('.fr-menu')
                summary = menu.locator('summary')
                summary.focus()
                page.keyboard.press('Enter')
                assert menu.get_attribute('open') is not None
                fits(page)
                page.keyboard.press('Escape')
                assert menu.get_attribute('open') is None
                assert summary.evaluate('(node) => node === document.activeElement')
                summary.click()
                page.mouse.click(4, 80)
                assert menu.get_attribute('open') is None
                page.screenshot(path=str(ARTIFACTS / f'home-{width}.png'), full_page=True)
                for slug, role, count, sections in ROLES:
                    page.goto(origin + BASE + FR + slug + '/')
                    assert page.locator('.fr-section').count() == sections
                    assert page.locator('[data-fr-topic]').count() == count
                    assert page.locator('.fr-role-tabs [aria-current]').inner_text() == role
                    page.locator('.fr-section > summary').first.click()
                    assert page.locator('[data-fr-topic]').first.is_visible()
                    fits(page)
                    if slug == 'colaboradores':
                        assert page.locator('.fr-section[data-section-kind="area"]').count() == 4
                        page.screenshot(path=str(ARTIFACTS / f'colaboradores-{width}.png'), full_page=True)
                    page.locator('[data-fr-topic]').first.click()
                    assert page.locator('.breadcrumbs').inner_text().find(role) >= 0
                    assert page.locator('.fr-role-tabs [aria-current]').inner_text() == role
                    page.locator('.fr-jump > summary').click()
                    assert page.locator('.fr-jump-panel a').count() == sections
                    fits(page)
                    page.locator('.fr-jump-panel a').nth(1).click()
                    assert page.locator('.fr-stage-content').count() == 1
                    fits(page)
                    tested.append(f'{width}px / {role}: hub, disclosure, canonical page, section navigation')
                page.goto(home + '#buscar')
                page.locator('#public-search-query').wait_for()
                page.wait_for_function('!document.querySelector("#public-search-query").disabled')
                page.locator('#public-search-query').fill('garantía')
                page.locator('#public-search-submit').click()
                page.wait_for_function('document.querySelector("#public-search-results").children.length > 0')
                page.locator('#guidance-start').click()
                assert page.locator('#guidance-panel').is_visible()
                assert not errors, errors
                context.close()
            context = browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 844})
            page = context.new_page()
            page.goto(home)
            page.locator('.fr-menu > summary').click()
            page.locator('.fr-menu-role').last.click()
            page.locator('.fr-section > summary').first.click()
            page.locator('[data-fr-topic]').first.click()
            assert page.locator('.fr-role-tabs [aria-current]').inner_text() == 'Colaboradores'
            tested.append('No JavaScript: menu, role hub, disclosure and canonical page work')
            context.close()
            browser.close()
    finally:
        server.shutdown()
    (ARTIFACTS / 'report.json').write_text(json.dumps({'passed': tested}, ensure_ascii=False, indent=2))
    print('\n'.join('PASS: ' + case for case in tested))


if __name__ == '__main__':
    main()
