"""Regresión de la galería pública a partir de los registros canónicos vinculados."""
import json
import os
from collections import Counter
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright, expect
from smoke_fr_navigation import ROOT, SITE, BASE, ARTIFACTS, Handler, fits


def expected_videos():
    fr = json.loads((ROOT / '_data/fr_tiktok_publicaciones.json').read_text())
    don = json.loads((ROOT / '_data/donacion_tiktok_publicaciones.json').read_text())
    rec = json.loads((ROOT / '_data/recompensa_tiktok_publicaciones.json').read_text())
    assembly = json.loads((ROOT / '_data/fr_ensamblaje_marketing.json').read_text())
    pieces = {item['code']: item for item in assembly['pieces']}
    assert all(pieces[video['piece_code']]['principal'] or pieces[video['piece_code']]['complementaria'] for video in fr['videos'])
    assert all(video['principal'] or video['complementaria'] for video in don['videos'])
    assert rec['category_code'] == 'REC' and rec['association_status'] == 'pending_review'
    assert all(video['principal'] or video['complementaria'] for video in rec['videos'])
    expected = {video['video_id']: 'Financiamiento Reembolsable' for video in fr['videos']}
    expected.update({video['video_id']: 'Donación' for video in don['videos']})
    expected.update({video['video_id']: 'Recompensa' for video in rec['videos']})
    assert len(expected) == len(fr['videos']) + len(don['videos']) + len(rec['videos'])
    return expected


def main():
    expected = expected_videos()
    assert len(expected) == 11, 'Se modificó el inventario de vídeos sin actualizar la prueba'
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(SITE)))
    Thread(target=server.serve_forever, daemon=True).start()
    home = f'http://127.0.0.1:{server.server_port}{BASE}/'
    passed = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE_PATH'))
            for width in (1280, 320):
                context = browser.new_context(viewport={'width': width, 'height': 900})
                page = context.new_page()
                errors = []
                requests = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                context.route('https://www.tiktok.com/player/**', lambda route: (requests.append(route.request.url), route.fulfill(content_type='text/html; charset=utf-8', body='<p>Vídeo de prueba</p>')))
                page.goto(home)
                cards = page.locator('.home-video-card')
                assert cards.count() == len(expected), f'{width}px: {cards.count()} tarjetas de {len(expected)}'
                ids = cards.evaluate_all('(items) => items.map((item) => item.dataset.videoId)')
                assert Counter(ids) == Counter(expected.keys()), ids
                assert cards.locator('a[href*="/@iskay.app/video/"]').count() == len(expected)
                assert cards.locator('a[href*="#media-"]').count() == len(expected)
                assert page.locator('.resource-card').count() == 2, 'Los diagramas originales deben mantenerse'
                expect(page.locator('#home-video-count')).to_have_text(f'{len(expected)} vídeos disponibles')
                assert not requests, 'No deben descargarse reproductores sin petición del usuario'
                fits(page)

                first = cards.first
                first.locator('.home-video-poster').focus()
                page.keyboard.press('Enter')
                expect(first.locator('iframe')).to_be_visible()
                expect(page.frame_locator('.home-video-card iframe').first.locator('p')).to_have_text('Vídeo de prueba')
                src = first.locator('iframe').get_attribute('src')
                assert 'autoplay=0' in src and 'loop=0' in src, src
                first.locator('.home-video-poster').click()
                expect(first.locator('iframe')).not_to_be_visible()

                category = page.locator('#home-video-category')
                category.select_option(label='Donación')
                expect(page.locator('#home-video-count')).to_have_text('3 vídeos disponibles')
                assert page.locator('.home-video-card:visible').count() == 3
                assert all(c == 'Donación' for c in page.locator('.home-video-card:visible').evaluate_all('(items) => items.map((item) => item.dataset.category)'))
                role = page.locator('#home-video-role')
                role.select_option(label='Donantes')
                expect(page.locator('#home-video-count')).to_have_text('1 vídeo disponible')
                stage = page.locator('#home-video-stage')
                stage_options = stage.locator('option').all_text_contents()
                assert len(stage_options) >= 2, stage_options
                stage.select_option(index=1)
                expect(page.locator('#home-video-count')).to_have_text('1 vídeo disponible')
                page.locator('#home-video-reset').click()
                expect(page.locator('#home-video-count')).to_have_text(f'{len(expected)} vídeos disponibles')
                assert page.locator('#home-video-reset').is_hidden()
                fits(page)
                assert not errors, errors
                page.screenshot(path=str(ARTIFACTS / f'galeria-multimedia-{width}.png'), full_page=True)
                context.close()
                passed.append(f'{width}px: 9 vídeos reales sin duplicados, acceso original y canónico, filtro categoría/rol/etapa, teclado y reproductor sin autoplay')

            context = browser.new_context(java_script_enabled=False, viewport={'width':320,'height':900})
            context.route('https://www.tiktok.com/player/**', lambda route: route.fulfill(content_type='text/html; charset=utf-8', body='<p>Vídeo de prueba</p>'))
            page = context.new_page()
            page.goto(home)
            assert page.locator('.home-video-card').count() == 9
            assert page.locator('#home-video-filters').is_hidden()
            page.locator('.home-video-poster').first.click()
            expect(page.locator('.home-video-card iframe').first).to_be_visible()
            fits(page)
            context.close()
            browser.close()
            passed.append('Sin JavaScript: las nueve fichas/vídeos y los reproductores nativos siguen siendo accesibles')
    finally:
        server.shutdown()
    (ARTIFACTS / 'home-video-gallery-report.json').write_text(json.dumps({'passed':passed}, ensure_ascii=False, indent=2))
    print('\n'.join('PASS: ' + line for line in passed))


if __name__ == '__main__':
    main()
