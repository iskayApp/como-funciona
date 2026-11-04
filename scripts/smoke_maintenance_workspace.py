"""Exercise the four real rendered views with an explicitly synthetic service report."""
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
import json
from playwright.sync_api import sync_playwright
from smoke_fr_navigation import ROOT, SITE, BASE, ARTIFACTS, Handler, fits
from smoke_category_base import report_fixture


def main():
    control=json.loads((SITE / 'mantenimiento/control_catalog.json').read_text())
    assert control['summary']['published']==99
    assert control['summary']['editorial']=={'unspecified':33,'approved':7,'pending_review':59}
    route_audit=json.loads((ARTIFACTS / 'maintenance-route-audit.json').read_text())
    assert route_audit['reachable']==99
    assert not route_audit['unreachable_topics']
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(SITE)))
    Thread(target=server.serve_forever,daemon=True).start()
    home=f'http://127.0.0.1:{server.server_port}'+BASE+'/'
    fixture=report_fixture()
    fixture['tiktok_inventory']={'videos':[{'video_id':'fixture-only','title':'Recurso sintético de prueba','status':'SIN VINCULAR'}]}
    passed=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            for width in (1280,390,320):
                context=browser.new_context(viewport={'width':width,'height':900})
                context.route('**/mantenimiento/status.json',lambda route:route.fulfill(json=fixture))
                page=context.new_page(); errors=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.goto(home+'mantenimiento/')
                page.locator('#workspace-filters').wait_for(state='visible')
                assert page.locator('[data-maint-view-link]').count()==4
                assert page.locator('[data-maint-view]:visible').count()==1
                assert page.locator('[data-maint-topic]').count()==99
                assert page.locator('.control-topic-button').count()==99
                page.locator('#control-query').fill('CF-FR-COL-003')
                assert page.locator('[data-maint-topic]:visible').count()==1
                page.locator('.control-topic-button:visible').click()
                assert page.locator('#topic-control').is_visible()
                assert 'Pendiente de revisión' in page.locator('#topic-control').inner_text()
                assert 'Sin referencia registrada' in page.locator('#topic-control').inner_text()
                assert page.locator('#topic-control-title').evaluate('(n)=>n===document.activeElement')
                fits(page)
                page.locator('[data-close-control]').click()
                page.locator('#control-clear').click()
                page.locator('#control-role').select_option('colaboradores')
                page.locator('[data-maint-view-link="m-revisiones"]').click()
                assert page.locator('#m-revisiones').is_visible()
                assert '27 fichas' in page.locator('#review-count').inner_text()
                assert page.locator('#review-records [data-control-record]').count()==20
                page.locator('#review-more').click()
                assert page.locator('#review-records [data-control-record]').count()==27
                page.locator('#control-clear').click()
                page.locator('#review-kind').select_option('unspecified')
                assert '33 fichas' in page.locator('#review-count').inner_text()
                sources=page.locator('#impact-source option').evaluate_all('(options)=>options.map(o=>o.value).filter(Boolean)')
                assert sources
                page.locator('#impact-source').select_option(sources[0])
                expected=sum(i['source']['label']==sources[0] for i in control['items'])
                assert page.locator('#impact-records [data-control-record]').count()==expected
                assert 'No hay cambios de guía registrados' in page.locator('#guide-change-records').inner_text()
                fits(page)
                page.locator('[data-maint-view-link="m-contenido"]').click()
                page.locator('#control-query').fill('FR-PRO-13')
                page.locator('.control-topic-button:visible').click()
                page.locator('[data-show-media]').click()
                assert page.locator('#m-multimedia').is_visible()
                page.wait_for_function('document.querySelector("#maint-search-results").textContent.includes("FR-PRO-13")')
                assert page.locator('#maint-search-results [data-copy-url]').count()>0
                page.wait_for_selector('#marketing-unlinked .maint-pending',state='attached')
                assert 'Recurso sintético de prueba' in page.locator('#marketing-unlinked').inner_text()
                assert page.locator('#maintenance-dashboard .maint-pending').count()==0
                fits(page)
                page.locator('[data-maint-view-link="m-publicacion"]').click()
                page.locator('#control-clear').click()
                assert page.locator('#publication-summary strong').all_text_contents()==['99','59','7','33']
                assert page.locator('#publication-records .workspace-tag').count()==60
                assert 'Sin comprobar' in page.locator('#publication-records').inner_text()
                page.screenshot(path=str(ARTIFACTS/f'maintenance-publication-{width}.png'),full_page=True)
                fits(page)
                page.locator('[data-maint-view-link="m-contenido"]').focus()
                page.keyboard.press('Enter')
                assert page.locator('#m-contenido').is_visible()
                page.locator('#control-category').select_option('donacion')
                assert page.locator('[data-maint-category="donacion"]').is_visible()
                assert page.locator('#control-role').is_disabled()
                page.locator('#control-clear').click()
                page.screenshot(path=str(ARTIFACTS/f'maintenance-content-{width}.png'),full_page=True)
                assert not errors,errors
                passed.append(f'{width}px: four views, scoped filters, control, 59/7/33 editorial states, source impact, existing sharing, service fixture, keyboard')
                context.close()
            context=browser.new_context(java_script_enabled=False,viewport={'width':320,'height':900})
            page=context.new_page(); page.goto(home+'mantenimiento/')
            assert page.locator('[data-maint-view]:visible').count()==4
            page.locator('[data-maint-role="promotores"] > summary').click()
            page.locator('[data-maint-role="promotores"] [data-maint-section] > summary').first.click()
            page.locator('[data-maint-role="promotores"] [data-maint-topic]').first.click()
            assert '/promotores/' in page.url
            fits(page); context.close(); passed.append('No JavaScript: four sections and native hierarchy remain navigable')
            context=browser.new_context()
            context.route('**/mantenimiento/control_catalog.json',lambda route:route.fulfill(status=503,body='Unavailable'))
            context.route('**/mantenimiento/status.json',lambda route:route.fulfill(status=503,body='Unavailable'))
            page=context.new_page(); page.goto(home+'mantenimiento/')
            page.wait_for_function('document.querySelector("#workspace-load-status").textContent.includes("No se pudo cargar")')
            assert page.locator('[data-maint-topic]').count()==99
            page.locator('[data-maint-view-link="m-multimedia"]').click()
            page.locator('#maint-search-text').fill('garantia')
            page.wait_for_function('document.querySelector("#maint-search-results").children.length > 0')
            context.close(); passed.append('Control/report outages preserve native navigation and independent marketing search')
            browser.close()
    finally:
        server.shutdown()
    (ARTIFACTS/'maintenance-workspace-report.json').write_text(json.dumps({'passed':passed,'service_report':'synthetic_fixture'},ensure_ascii=False,indent=2))
    print('\n'.join('PASS: '+line for line in passed))


if __name__=='__main__': main()
