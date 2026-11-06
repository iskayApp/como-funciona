"""Exercise the maintenance hub using real catalogs and explicitly synthetic reports."""
import csv
import io
import json
import os
from collections import Counter
from datetime import datetime, timezone
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright, expect
from smoke_fr_navigation import ROOT, SITE, BASE, ARTIFACTS, Handler, fits
from smoke_category_base import report_fixture


def advanced(page):
    details=page.locator('.workspace-filter-details')
    if not details.evaluate('(node) => node.open'):
        details.locator('summary').click()


def check_width(page, home, control, width):
    page.goto(home+'mantenimiento/')
    page.locator('#workspace-filters').wait_for(state='visible')
    assert page.locator('[data-maint-view-link]').count()==5
    expect(page.locator('[data-maint-view]:visible')).to_have_count(1)
    expect(page.locator('#m-resumen')).to_be_visible()
    expect(page.locator('#overview-metrics .overview-metric > strong').first).to_have_text('139')
    assert page.locator('[data-maint-topic]').count()==139
    assert page.locator('.control-topic-button').count()==139
    assert 'Donación' not in page.locator('#overview-preparation').inner_text()
    fits(page)
    page.screenshot(path=str(ARTIFACTS/f'maintenance-panorama-{width}.png'),full_page=True)
    page.locator('[data-maint-view-link="m-contenido"]').click()
    page.locator('#control-query').fill('CF-FR-COL-003')
    expect(page.locator('[data-maint-topic]:visible')).to_have_count(1)
    origin=page.locator('.control-topic-button:visible')
    origin.click()
    expect(page.locator('#topic-control')).to_be_visible()
    assert 'Pendiente de revisión' in page.locator('#topic-control').inner_text()
    expect(page.locator('#topic-control-title')).to_be_focused()
    page.keyboard.press('Escape')
    expect(page.locator('#topic-control')).not_to_be_visible()
    expect(origin).to_be_focused()
    page.locator('#control-clear').click()
    advanced(page)
    page.locator('#control-category').select_option('financiamiento-reembolsable')
    page.locator('#control-role').select_option('colaboradores')
    page.locator('[data-maint-view-link="m-publicacion"]').click()
    expect(page.locator('#publication-summary .overview-metric > strong').first).to_have_text('29')
    expect(page.locator('#publication-freshness')).to_contain_text('Informe vigente · misma versión')
    expect(page.locator('#publication-records [data-tone="good"]').filter(has_text='Técnico')).to_have_count(20)
    page.locator('[data-maint-view-link="m-revisiones"]').click()
    expect(page.locator('#review-count')).to_contain_text('de 27 fichas')
    expect(page.locator('#review-records [data-control-record]')).to_have_count(20)
    page.locator('#review-more').click()
    expect(page.locator('#review-records [data-control-record]')).to_have_count(27)
    opener=page.locator('#review-records [data-open-control]').first
    opener.click()
    assert page.url.split('#')[-1]=='m-revisiones'
    page.locator('[data-close-control]').click()
    expect(opener).to_be_focused()
    assert page.url.split('#')[-1]=='m-revisiones'
    with page.expect_download() as download:
        page.locator('#workspace-export').click()
    rows=list(csv.reader(io.StringIO(download.value.path().read_text(encoding='utf-8-sig')),delimiter=';'))
    assert len(rows)==28, len(rows)
    assert all(row[3]=='Colaboradores' for row in rows[1:])
    saved=page.url
    page.reload()
    page.locator('#workspace-filters').wait_for(state='visible')
    assert page.locator('#control-category').input_value()=='financiamiento-reembolsable'
    assert page.locator('#control-role').input_value()=='colaboradores'
    assert page.url.split('#')[-1]=='m-revisiones'
    page.locator('#workspace-copy').click()
    expect(page.locator('#workspace-feedback')).to_contain_text('Vista copiada')
    assert page.evaluate('navigator.clipboard.readText()')==page.url
    page.locator('#control-clear').click()
    page.locator('#review-kind').select_option('gap:guide_version')
    expect(page.locator('#review-count')).to_contain_text('de 139 fichas')
    page.locator('#review-kind').select_option('gap:content_version')
    expect(page.locator('#review-count')).to_contain_text('de 30 fichas')
    page.locator('#review-kind').select_option('unverified')
    unknown=sum(bool(i['unverified_asset_ids']) for i in control['items'])
    expect(page.locator('#review-count')).to_contain_text(f'de {unknown} fichas')
    sources=Counter(i['source']['label'] for i in control['items'])
    source=max(sources,key=sources.get)
    page.locator('#impact-source').select_option(source)
    expect(page.locator('#impact-records [data-control-record]')).to_have_count(20)
    expect(page.locator('#impact-count')).to_contain_text(f'de {sources[source]} fichas')
    page.locator('#impact-more').click()
    expect(page.locator('#impact-records [data-control-record]')).to_have_count(40)
    with page.expect_download() as download:
        page.locator('#impact-export').click()
    impact_rows=list(csv.reader(io.StringIO(download.value.path().read_text(encoding='utf-8-sig')),delimiter=';'))
    assert len(impact_rows)==sources[source]+1
    assert all(row[2]==source for row in impact_rows[1:])
    page.reload()
    page.locator('#workspace-filters').wait_for(state='visible')
    assert page.locator('#impact-source').input_value()==source
    expect(page.locator('#impact-count')).to_contain_text(f'de {sources[source]} fichas')
    advanced(page)
    page.locator('#control-category').select_option('financiamiento-reembolsable')
    page.locator('[data-maint-view-link="m-multimedia"]').click()
    expect(page.locator('.media-resource-card')).to_have_count(8)
    page.locator('#media-provider').select_option('tiktok')
    expect(page.locator('.media-resource-card')).to_have_count(6)
    page.locator('#media-provider').select_option('')
    page.locator('#maint-search-text').fill('PRO-EDU-01')
    expect(page.locator('.media-resource-card')).to_have_count(1)
    page.locator('#maint-search-clear').click()
    page.locator('#media-kind').select_option('video')
    expect(page.locator('.media-resource-card')).to_have_count(6)
    with page.expect_download() as download:
        page.locator('#workspace-export').click()
    assert len(list(csv.reader(io.StringIO(download.value.path().read_text(encoding='utf-8-sig')),delimiter=';')))==7
    page.locator('#maint-search-clear').click()
    page.locator('[data-media-mode="fichas"]').click()
    expect(page.locator('.maint-search-result')).to_have_count(12)
    page.locator('#maint-search-more').click()
    expect(page.locator('.maint-search-result')).to_have_count(24)
    page.locator('#maint-search-text').fill('FR-PRO-13')
    expect(page.locator('.maint-search-result')).to_have_count(1)
    page.locator('.maint-search-result .media-placements > summary').click()
    assert page.locator('#maint-search-results [data-copy-url]').count()>=3
    page.locator('#maint-search-results [data-copy-url]').first.click()
    expect(page.locator('#maint-search-feedback')).to_contain_text('Enlace copiado')
    page.locator('#maint-search-clear').click()
    page.locator('[data-media-mode="pieces"]').click()
    expect(page.locator('#maint-search-count')).to_contain_text('de 61 piezas')
    expect(page.locator('.piece-card')).to_have_count(12)
    page.locator('#maint-search-text').fill('PRO-EDU-01')
    expect(page.locator('.piece-card')).to_have_count(1)
    page.locator('#media-kind').select_option('unverified')
    expect(page.locator('.piece-card')).to_have_count(1)
    page.locator('[data-maint-view-link="m-contenido"]').click()
    page.locator('#control-query').fill('CF-FR-COL-003')
    page.go_back()
    expect(page.locator('#m-multimedia')).to_be_visible()
    assert page.locator('#control-query').input_value()==''
    assert page.locator('#maint-search-text').input_value()=='PRO-EDU-01'
    expect(page.locator('.piece-card')).to_have_count(1)
    page.locator('#maint-search-clear').click()
    assert 'Pendientes' in page.locator('#marketing-unlinked').inner_text()
    # Keep FR's resource and piece counts protected, then exercise Donación separately.
    page.locator('#control-category').select_option('donacion')
    page.locator('[data-media-mode="resources"]').click()
    expect(page.locator('.media-resource-card')).to_have_count(3)
    page.locator('#media-provider').select_option('tiktok')
    expect(page.locator('.media-resource-card')).to_have_count(3)
    page.locator('#maint-search-clear').click()
    page.locator('[data-media-mode="fichas"]').click()
    expect(page.locator('#maint-search-count')).to_contain_text('de 40 fichas')
    expect(page.locator('.maint-search-result')).to_have_count(12)
    page.locator('[data-maint-view-link="m-revisiones"]').click()
    page.locator('#review-kind').select_option('pending')
    expect(page.locator('#review-count')).to_contain_text('de 40 fichas')
    page.locator('[data-maint-view-link="m-multimedia"]').click()
    fits(page)
    page.evaluate('window.scrollTo(0,0)')
    page.screenshot(path=str(ARTIFACTS/f'maintenance-library-{width}.png'),full_page=True)


def main():
    control=json.loads((SITE/'mantenimiento/control_catalog.json').read_text())
    assert control['summary']['published']==139
    assert Counter(item['category'] for item in control['items'])=={'Financiamiento Reembolsable':99,'Donación':40}
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(SITE)))
    Thread(target=server.serve_forever,daemon=True).start()
    home=f'http://127.0.0.1:{server.server_port}'+BASE+'/'
    fixture=report_fixture()
    fixture['generated_at']=datetime.now(timezone.utc).isoformat()
    fixture['revision']=control['revision']
    fixture['services']['tiktok']={'status':'OK','detail':'Escenario simulado de interfaz; no consulta TikTok.','recent_videos_checked':1}
    fixture['tiktok_inventory']={'complete':True,'videos':[{'video_id':'fixture-only','title':'Recurso sintético de prueba','status':'SIN VINCULAR'}]}
    for item in fixture['items']: item['status']='OK'
    passed=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXECUTABLE_PATH'))
            for width in (1440,768,390,320):
                context=browser.new_context(viewport={'width':width,'height':1000},permissions=['clipboard-read','clipboard-write'],reduced_motion='reduce')
                context.route('**/mantenimiento/status.json',lambda route:route.fulfill(json=fixture))
                page=context.new_page(); errors=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                try:
                    check_width(page,home,control,width)
                    assert not errors, errors
                except Exception:
                    page.screenshot(path=str(ARTIFACTS/f'maintenance-failure-{width}.png'),full_page=True)
                    (ARTIFACTS/f'maintenance-failure-{width}.json').write_text(json.dumps({'url':page.url,'errors':errors},ensure_ascii=False))
                    raise
                passed.append(f'{width}px: panorama, filtered totals, persistent URLs, contextual drawer, CSV, unique resources, pagination, provenance and clipboard')
                context.close()
            # Historical success cannot become a current success or verified zero.
            stale={**fixture,'generated_at':'2020-01-01T00:00:00Z','tiktok_inventory':{'videos':[]}}
            context=browser.new_context()
            context.route('**/mantenimiento/status.json',lambda route:route.fulfill(json=stale))
            page=context.new_page();page.goto(home+'mantenimiento/#m-publicacion')
            expect(page.locator('#publication-freshness')).to_contain_text('anterior')
            assert page.locator('#publication-records [data-tone="good"]').filter(has_text='Técnico').count()==0
            expect(page.locator('#marketing-unlinked')).to_contain_text('Pendientes sin comprobar')
            assert 'sin pendientes' not in page.locator('#marketing-unlinked').inner_text().lower()
            context.close();passed.append('Historical report and unknown inventory never present success or a false zero')
            context=browser.new_context(java_script_enabled=False,viewport={'width':320,'height':900})
            page=context.new_page();page.goto(home+'mantenimiento/')
            assert page.locator('[data-maint-view]:visible').count()==5
            group=page.locator('[data-maint-category="donacion"] [data-maint-role="promotores"]')
            group.locator(':scope > summary').click()
            group.locator('[data-maint-section] > summary').first.click()
            group.locator('[data-maint-topic]').first.click()
            assert '/donacion/promotores/' in page.url
            fits(page);context.close();passed.append('No JavaScript: five sections and native hierarchy remain navigable')
            context=browser.new_context()
            context.route('**/mantenimiento/control_catalog.json',lambda route:route.fulfill(status=503,body='Unavailable'))
            context.route('**/mantenimiento/status.json',lambda route:route.fulfill(status=503,body='Unavailable'))
            page=context.new_page();page.goto(home+'mantenimiento/')
            expect(page.locator('#workspace-load-status')).to_contain_text('No se pudo cargar')
            assert page.locator('[data-maint-topic]').count()==139
            page.locator('[data-maint-view-link="m-multimedia"]').click()
            page.locator('#maint-search-text').fill('garantia')
            expect(page.locator('#maint-search-count')).to_contain_text('Mostrando')
            context.close();passed.append('Independent catalog remains usable when control and technical reports fail')
            browser.close()
    finally: server.shutdown()
    (ARTIFACTS/'maintenance-workspace-report.json').write_text(json.dumps({'passed':passed,'service_report':'synthetic_fixture'},ensure_ascii=False,indent=2))
    print('\n'.join('PASS: '+line for line in passed))


if __name__=='__main__': main()
