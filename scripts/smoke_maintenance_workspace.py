"""Exercise the four rendered views; service reports are synthetic fixtures."""
import os
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
import json
from playwright.sync_api import sync_playwright, expect
from smoke_fr_navigation import ROOT, SITE, BASE, ARTIFACTS, Handler, fits
from smoke_category_base import report_fixture


def check_width(page, home, control, width):
    page.goto(home+'mantenimiento/')
    page.locator('#workspace-filters').wait_for(state='visible')
    assert page.locator('[data-maint-view-link]').count()==4
    expect(page.locator('[data-maint-view]:visible')).to_have_count(1)
    assert page.locator('[data-maint-topic]').count()==99
    assert page.locator('.control-topic-button').count()==99
    page.locator('#control-query').fill('CF-FR-COL-003')
    expect(page.locator('[data-maint-topic]:visible')).to_have_count(1)
    page.locator('.control-topic-button:visible').click()
    expect(page.locator('#topic-control')).to_be_visible()
    assert 'Pendiente de revisión' in page.locator('#topic-control').inner_text()
    assert 'Sin referencia registrada' in page.locator('#topic-control').inner_text()
    expect(page.locator('#topic-control-title')).to_be_focused()
    fits(page)
    page.locator('[data-close-control]').click()
    page.locator('#control-clear').click()
    page.locator('#control-role').select_option('colaboradores')
    page.locator('[data-maint-view-link="m-revisiones"]').click()
    expect(page.locator('#m-revisiones')).to_be_visible()
    expect(page.locator('#review-count')).to_contain_text('27 fichas')
    expect(page.locator('#review-records [data-control-record]')).to_have_count(20)
    page.locator('#review-more').click()
    expect(page.locator('#review-records [data-control-record]')).to_have_count(27)
    page.locator('#control-clear').click()
    page.locator('#review-kind').select_option('unspecified')
    expect(page.locator('#review-count')).to_contain_text('33 fichas')
    sources=page.locator('#impact-source option').evaluate_all('(options)=>options.map(o=>o.value).filter(Boolean)')
    assert sources
    page.locator('#impact-source').select_option(sources[0])
    expected=sum(i['source']['label']==sources[0] for i in control['items'])
    expect(page.locator('#impact-records [data-control-record]')).to_have_count(expected)
    assert 'No hay cambios de guía registrados' in page.locator('#guide-change-records').inner_text()
    fits(page)
    page.locator('[data-maint-view-link="m-contenido"]').click()
    expect(page.locator('#m-contenido')).to_be_visible()
    page.locator('#control-query').fill('FR-PRO-13')
    page.locator('.control-topic-button:visible').click()
    page.locator('[data-show-media]').click()
    expect(page.locator('#m-multimedia')).to_be_visible()
    expect(page.locator('#maint-search-results')).to_contain_text('FR-PRO-13')
    assert page.locator('#maint-search-results [data-copy-url]').count()>0
    page.wait_for_selector('#marketing-unlinked .maint-pending',state='attached')
    assert 'Recurso sintético de prueba' in page.locator('#marketing-unlinked').inner_text()
    assert page.locator('#maintenance-dashboard .maint-pending').count()==0
    fits(page)
    page.locator('[data-maint-view-link="m-publicacion"]').click()
    expect(page.locator('#m-publicacion')).to_be_visible()
    page.locator('#control-clear').click()
    expect(page.locator('#publication-summary strong')).to_have_text(['99','59','7','33'])
    expect(page.locator('#publication-records .workspace-tag')).to_have_count(60)
    assert 'Sin comprobar' in page.locator('#publication-records').inner_text()
    page.screenshot(path=str(ARTIFACTS/f'maintenance-publication-{width}.png'),full_page=True)
    fits(page)
    page.locator('[data-maint-view-link="m-contenido"]').focus()
    page.keyboard.press('Enter')
    expect(page.locator('#m-contenido')).to_be_visible()
    page.locator('#control-category').select_option('donacion')
    expect(page.locator('[data-maint-category="donacion"]')).to_be_visible()
    expect(page.locator('#control-role')).to_be_disabled()
    page.locator('#control-clear').click()
    page.screenshot(path=str(ARTIFACTS/f'maintenance-content-{width}.png'),full_page=True)


def main():
    control=json.loads((SITE / 'mantenimiento/control_catalog.json').read_text())
    assert control['summary']['published']==99
    assert control['summary']['editorial']=={'unspecified':33,'approved':7,'pending_review':59}
    route_audit=json.loads((ARTIFACTS / 'maintenance-route-audit.json').read_text())
    assert route_audit['reachable']==99 and not route_audit['unreachable_topics']
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(SITE)))
    Thread(target=server.serve_forever,daemon=True).start()
    home=f'http://127.0.0.1:{server.server_port}'+BASE+'/'
    fixture=report_fixture()
    fixture['tiktok_inventory']={'videos':[{'video_id':'fixture-only','title':'Recurso sintético de prueba','status':'SIN VINCULAR'}]}
    passed=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=os.environ.get("CHROMIUM_EXECUTABLE_PATH"))
            for width in (1280,390,320):
                context=browser.new_context(viewport={'width':width,'height':900})
                context.route('**/mantenimiento/status.json',lambda route:route.fulfill(json=fixture))
                page=context.new_page(); errors=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                try:
                    check_width(page,home,control,width)
                    assert not errors,errors
                except Exception:
                    page.screenshot(path=str(ARTIFACTS/f'maintenance-failure-{width}.png'),full_page=True)
                    (ARTIFACTS/f'maintenance-failure-{width}.json').write_text(json.dumps({'url':page.url,'errors':errors,'panels':page.locator('[data-maint-view]').evaluate_all('(nodes)=>nodes.map(n=>({id:n.id,hidden:n.hidden}))')},ensure_ascii=False,indent=2))
                    raise
                passed.append(f'{width}px: four views, filters, ficha controls, editorial states, impact, sharing, service fixture and keyboard')
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
            expect(page.locator('#workspace-load-status')).to_contain_text('No se pudo cargar')
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
