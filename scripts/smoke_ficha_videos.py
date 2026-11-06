"""Check every published ficha and exercise the shared player without contacting TikTok."""
import json
import os
from collections import Counter
from functools import partial
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlsplit, parse_qs
from playwright.sync_api import sync_playwright, expect
from smoke_fr_navigation import ROOT, SITE, BASE, ARTIFACTS, Handler, fits


class VideoPage(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.states = []
        self.ids = []
        self.unavailable = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section' and 'ficha-videos' in attrs.get('class', '').split():
            self.states.append(attrs.get('data-video-status'))
        if tag == 'figure' and attrs.get('data-video-id'):
            self.ids.append(attrs['data-video-id'])

    def handle_data(self, text):
        if 'Vídeo explicativo aún no disponible' in text:
            self.unavailable = True


def expected_videos():
    """Use the editorial registry independently of the generated catalog."""
    registry = json.loads((ROOT / '_data/fr_tiktok_publicaciones.json').read_text())
    assembly = json.loads((ROOT / '_data/fr_ensamblaje_marketing.json').read_text())
    pieces = {piece['code']: piece for piece in assembly['pieces']}
    expected = {}
    for video in registry['videos']:
        piece = pieces[video['piece_code']]
        for relation in ('principal', 'complementaria'):
            for code in piece[relation]:
                expected.setdefault(code, []).append(video['video_id'])
    return expected


def main():
    catalog = json.loads((SITE / 'mantenimiento/share_catalog.json').read_text())
    topics = [item for item in catalog['items'] if item.get('public_searchable') is not False]
    expected = expected_videos()
    assert topics, 'No se generaron fichas publicables'
    assert set(expected) <= {item['code'] for item in topics}, 'Faltan fichas con vídeos registrados'
    states = Counter()
    for item in topics:
        route = urlsplit(item['canonical_url']).path[len(BASE):].lstrip('/')
        page = VideoPage((SITE / route / 'index.html').read_text())
        video_ids = expected.get(item['code'], [])
        state = 'available' if video_ids else 'unavailable'
        assert page.states == [state], (item['code'], page.states)
        assert Counter(page.ids) == Counter(video_ids), item['code']
        assert page.unavailable == (not video_ids), item['code']
        states[state] += 1
    passed = [f'{len(topics)} fichas: {states["available"]} con reproductores y {states["unavailable"]} con aviso; ninguna asociación inventada']
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(SITE)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    samples = ('FR-PRO-01', 'FR-PRO-02', 'FR-PRO-03', 'CF-FR-INV-001', 'CF-FR-COL-001')
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE_PATH'))
            for width in (1280, 320):
                context = browser.new_context(viewport={'width':width, 'height':900})
                page = context.new_page()
                # This controlled response tests our button and iframe, not TikTok availability.
                requests = []
                def player(route):
                    requests.append(route.request.url)
                    route.fulfill(content_type='text/html', body='<p>Reproductor de prueba</p>')
                context.route('https://www.tiktok.com/player/**', player)
                for code in samples:
                    item = next(item for item in topics if item['code'] == code)
                    requests.clear()
                    page.goto(origin + urlsplit(item['canonical_url']).path)
                    cards = page.locator('.fr-tiktok-card')
                    assert cards.count() == len(expected.get(code, []))
                    section = page.locator('.ficha-videos')
                    section.scroll_into_view_if_needed()
                    fits(page)
                    if cards.count():
                        assert not requests, (code, requests)
                        card = cards.first
                        button = card.locator('summary')
                        expect(button).to_have_text('Reproducir vídeo explicativo')
                        assert not card.locator('details').evaluate('(node) => node.open')
                        assert not card.locator('iframe').is_visible()
                        button.focus()
                        page.keyboard.press('Enter')
                        expect(card.locator('iframe')).to_be_visible()
                        expect(page.frame_locator('iframe').first.locator('p')).to_have_text('Reproductor de prueba')
                        src = card.locator('iframe').get_attribute('src')
                        assert parse_qs(urlsplit(src).query)['autoplay'] == ['0']
                        assert parse_qs(urlsplit(src).query)['loop'] == ['0']
                        assert card.locator('a[href*="/@iskay.app/video/"]').count() == 1
                        anchor = card.get_attribute('id')
                        assert page.locator(f'.share-link-destination[href$="#{anchor}"]').count() == 1
                        page.keyboard.press('Enter')
                        expect(card.locator('iframe')).not_to_be_visible()
                    else:
                        expect(section).to_contain_text('Vídeo explicativo aún no disponible')
                        assert section.locator('summary, iframe, button').count() == 0
                    fits(page)
                    if code in ('FR-PRO-02', 'CF-FR-INV-001'):
                        page.screenshot(path=str(ARTIFACTS / f'videos-{code.lower()}-{width}.png'))
                context.close()
                passed.append(f'{width}px: relaciones principales, complementarias, mixtas y fichas sin vídeo; teclado, apertura/cierre, enlace original y ancla para compartir')
            context = browser.new_context(java_script_enabled=False, viewport={'width':320,'height':900})
            context.route('https://www.tiktok.com/player/**', lambda route: route.fulfill(content_type='text/html', body='<p>Reproductor de prueba</p>'))
            page = context.new_page()
            item = next(item for item in topics if item['code'] == 'FR-PRO-02')
            page.goto(origin + urlsplit(item['canonical_url']).path)
            card = page.locator('.fr-tiktok-card').first
            card.locator('summary').click()
            expect(card.locator('iframe')).to_be_visible()
            fits(page)
            context.close()
            browser.close()
            passed.append('Sin JavaScript: el reproductor complementario funciona mediante el desplegable nativo')
    finally:
        server.shutdown()
    (ARTIFACTS / 'ficha-videos-report.json').write_text(json.dumps({'passed':passed}, ensure_ascii=False, indent=2))
    print('\n'.join('PASS: ' + line for line in passed))


if __name__ == '__main__':
    main()
