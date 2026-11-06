/* Maintenance workspace: public projections, explicit scope and reversible navigation. */
(() => {
  'use strict';
  const C = typeof module !== 'undefined' && module.exports ? require('./maintenance-core.js') : window.MaintenanceCore;
  const {norm,filterItems,affectedBy,reviewMatches,technicalLabel,node} = C;
  if (typeof module !== 'undefined' && module.exports) module.exports = {norm,filterItems,affectedBy,reviewMatches,technicalLabel};
  if (typeof document === 'undefined') return;
  const $ = id => document.getElementById(id), root = $('maintenance-workspace');
  if (!root) return;
  const editorial = {approved:'Aprobada explícitamente',pending_review:'Pendiente de revisión',changes_requested:'Cambios solicitados',draft:'Borrador',unspecified:'Sin estado explícito'};
  const gaps = {editorial_state:'Registrar el estado editorial',functional_source:'Identificar la fuente funcional',source_section:'Identificar la sección de la fuente',guide_version:'Identificar la versión de guía',content_version:'Registrar la versión de ficha'};
  const comparisons = {no_reference:'Sin referencia en preparación',same_content:'Misma huella de contenido',different_content:'Contenido diferente',same_version_unverified:'Misma versión, contenido sin contrastar',different_version:'Versiones diferentes',unverified:'Sin datos suficientes'};
  const fields = {query:'control-query',category:'control-category',role:'control-role',section:'control-section'};
  let data = null, selected = [], report = window.__maintenanceData || null;
  let reviewLimit = 20, publicationLimit = 20, impactLimit = 20, activeView = 'm-resumen', snapshot = null;
  let openCode = null, opener = null, originScroll = 0;
  const panels = [...root.querySelectorAll('[data-maint-view]')], links = [...root.querySelectorAll('[data-maint-view-link]')];
  const paragraph = text => node('p',{class:'maint-meta'},text);
  const button = (text,attrs={}) => node('button',{type:'button',class:'workspace-button',...attrs},text);
  const dateLabel = value => value && Number.isFinite(Date.parse(value)) ? new Date(value).toLocaleString('es-ES') : 'Sin fecha registrada';
  const filters = () => Object.fromEntries(Object.entries(fields).map(([key,id])=>[key,$(id).value]));
  const publicLink = (value,label) => {const url=C.safeURL(value,location.href); return url ? node('a',{href:url,target:'_blank',rel:'noopener noreferrer'},label) : null;};
  function choices(select,rows,label) {
    const previous=select.value;
    select.replaceChildren(new Option(label,''));
    rows.forEach(([value,title])=>select.add(new Option(title,value)));
    if (rows.some(([value])=>value===previous)) select.value=previous;
  }
  function dependentFilters() {
    if (!data) return;
    const category=$('control-category').value;
    const roles=new Map(data.categories.filter(c=>!category || c.id===category).flatMap(c=>c.roles.map(r=>[r.id,r.name])));
    choices($('control-role'),[...roles],'Todos los roles'); $('control-role').disabled=!roles.size;
    const scoped=filterItems(data.items,{category,role:$('control-role').value});
    choices($('control-section'),[...new Map(scoped.map(i=>[i.stage_url,i.role+' · '+i.stage]))],'Todas las secciones');
    $('control-section').disabled=!scoped.length;
  }
  function writeURL() {
    const url=new URL(location.href);
    Object.entries(filters()).forEach(([key,value])=>value ? url.searchParams.set(key,value) : url.searchParams.delete(key));
    const queue=$('review-kind').value;
    queue==='pending' ? url.searchParams.delete('queue') : url.searchParams.set('queue',queue);
    openCode ? url.searchParams.set('topic',openCode) : url.searchParams.delete('topic');
    [['source',$('impact-source').value],['sourceSection',$('impact-section').value]].forEach(([key,value])=>value?url.searchParams.set(key,value):url.searchParams.delete(key));
    history.replaceState(null,'',url);
  }
  function showView() {
    const aliases={'maintenance-search':'m-multimedia','maintenance-dashboard':'m-publicacion','maintenance-structure':'m-contenido','topic-control':'m-contenido'};
    const hash=location.hash.slice(1);
    activeView=panels.some(p=>p.id===hash) ? hash : (aliases[hash] || 'm-resumen');
    panels.forEach(p=>{p.hidden=p.id!==activeView;});
    links.forEach(link=>{if(link.dataset.maintViewLink===activeView)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');});
    if (data) window.dispatchEvent(new CustomEvent('maintenance:scope',{detail:{items:selected,codes:selected.map(i=>i.code),filters:filters(),revision:data.revision,view:activeView}}));
  }
  function navigate(view) {location.hash=view;showView();}
  window.addEventListener('hashchange',showView); showView();
  const freshness=()=>C.reportState(report,data?.revision);
  function technicalFor(i) {
    const fresh=freshness();
    if (!fresh.current) return {label:report ? 'Sin comprobar · informe anterior' : 'Sin comprobar',kind:'unknown'};
    const entry=report?.items?.find(r=>r.code===i.code);
    if (entry?.content_version != null && i.content_version != null && String(entry.content_version)!==String(i.content_version)) return {label:'Sin comprobar · versión diferente',kind:'unknown'};
    return {label:technicalLabel(entry),kind:entry?.status==='OK' ? 'good' : entry?.status==='ROTO' ? 'danger' : 'unknown'};
  }
  function tags(i) {
    const technical=technicalFor(i);
    return node('div',{class:'workspace-tags'},
      node('span',{class:'workspace-tag', 'data-tone':i.editorial_status==='approved'?'good':i.editorial_status==='pending_review'?'warning':'neutral'},node('strong',{},'Editorial: '),editorial[i.editorial_status] || editorial.unspecified),
      node('span',{class:'workspace-tag'},node('strong',{},'Publicación: '),({test_published:'Para pruebas',published:'Publicada'})[i.publication_status] || 'Sin estado de publicación'),
      node('span',{class:'workspace-tag','data-tone':technical.kind},node('strong',{},'Técnico: '),technical.label));
  }
  function metric(count,label,detail,tone) {
    return node('div',{class:'overview-metric','data-tone':tone || 'blue'},node('span',{class:'metric-label'},label),node('strong',{},count),node('span',{class:'metric-detail'},detail));
  }
  function priority(count,title,detail,queue,tone='blue') {
    return node('button',{type:'button',class:'priority-action','data-queue':queue,'data-tone':tone,...(!count?{disabled:''}:{})},node('span',{class:'priority-count'},count),node('span',{},node('strong',{},title),node('small',{},detail)),node('span',{class:'priority-arrow','aria-hidden':'true'},'→'));
  }
  function preparation(target) {
    const rows=data.category_preparation || [], phases=['classified','organized','identified','developed'], labels=['Clasificar','Organizar','Identificar','Desarrollar'];
    const cards=rows.map(row=>{
      const phase=phases.indexOf(row.phase);
      return node('article',{class:'preparation-card'},node('div',{class:'panel-heading'},node('h4',{},row.title),node('span',{class:'workspace-tag','data-tone':'warning'},row.review_status==='approved'?'Fase aprobada':'Preparada para revisión')),
        node('div',{class:'phase-track'},labels.map((label,i)=>node('span',{'data-active':String(i===phase)},node('b',{},String(i+1).padStart(2,'0')),label))),
        paragraph((row.roles || []).map(r=>r.name+': '+r.records+' registros').join(' · ')),
        node('div',{class:'preparation-footer'},node('span',{},'Preparación documental · No publicada'),publicLink(row.reference_url,'Ver referencia →')));
    });
    const topicRows=(data.preparation || []).map(p=>node('article',{class:'workspace-record'},node('div',{},node('h3',{},p.title || p.code),paragraph(p.code+' · '+p.phase+' · No publicada'),publicLink(p.reference_url,'Consultar referencia'))));
    $(target).replaceChildren(...(cards.length || topicRows.length ? [...cards,...topicRows] : [paragraph('No hay avances publicables registrados. Consulta la fuente editorial para conocer el trabajo en preparación.')]));
  }
  function overview() {
    if (!data) return;
    const s=C.summarize(selected), resources=C.uniqueResources(sharedForSelection());
    $('overview-metrics').replaceChildren(metric(s.total,'Fichas publicadas','Dentro de los filtros actuales'),metric(s.pending,'Pendientes editoriales','Una cola con siguiente acción','amber'),metric(s.unspecified,'Sin estado explícito','Pendiente de registrar','slate'),metric(s.withVideo,'Fichas con vídeo',sharedReady ? resources.filter(r=>r.type==='video').length+' vídeos únicos vinculados' : 'Inventario de recursos no disponible','teal'));
    $('nav-review-count').textContent=String(s.pending);
    $('overview-priorities').replaceChildren(priority(s.pending,'Continuar la revisión editorial','Abrir la cola y consultar su fuente','pending','amber'),priority(s.unspecified,'Registrar decisiones editoriales','Distinguir lo aprobado de lo no registrado','unspecified','slate'),priority(selected.filter(i=>i.metadata_gaps.includes('guide_version')).length,'Identificar la versión de guía','Un mismo dato pendiente en varias fichas','gap:guide_version'),priority(s.unverified,'Contrastar la vigencia de los recursos',selected.reduce((sum,i)=>sum+(i.unverified_asset_ids?.length||0),0)+' ubicaciones sin versión de origen · '+s.unverified+' fichas','unverified','teal'));
    const total=s.total || 1;
    const bars=node('div',{class:'editorial-distribution','aria-hidden':'true'},...[[s.approved,'good'],[s.pending,'warning'],[s.unspecified,'neutral']].map(([count,tone])=>node('span',{'data-tone':tone,style:'width:'+(count/total*100)+'%'})));
    $('overview-editorial').replaceChildren(bars,node('div',{class:'distribution-legend'},...[[s.approved,'Aprobadas','good'],[s.pending,'Pendientes','warning'],[s.unspecified,'Sin estado','neutral']].map(([count,label,tone])=>node('span',{'data-tone':tone},node('i',{'aria-hidden':'true'}),label,node('strong',{},count)))),paragraph('Publicación y aprobación editorial se consultan por separado.'));
    const percent=s.total ? Math.round(s.withVideo/s.total*100) : 0;
    $('overview-coverage').replaceChildren(node('div',{class:'coverage-composition'},node('div',{class:'coverage-ring',style:'--coverage:'+percent+'%'},node('strong',{},percent+'%'),node('span',{},'con vídeo')),node('div',{},node('strong',{class:'coverage-count'},s.withVideo+' de '+s.total+' fichas'),paragraph(s.noVideo+' sin vídeo publicado'),button('Explorar recursos →',{'data-go-view':'m-multimedia'}))),paragraph('La cobertura multimedia no determina la aprobación editorial.'));
    preparation('overview-preparation'); preparation('preparation-records');
  }
  let sharedItems=[], sharedReady=false;
  function sharedForSelection() {const codes=new Set(selected.map(i=>i.code));return sharedItems.filter(i=>codes.has(i.code));}
  function record(i,detail,withTags=false) {
    return node('article',{class:'workspace-record','data-control-record':i.code},node('div',{class:'record-main'},node('span',{class:'record-code'},i.code),node('h3',{},i.title),paragraph(i.role+' · '+i.stage),detail?node('p',{class:'record-reason'},detail):null,withTags?tags(i):null),button('Ver control →',{'data-open-control':i.code}));
  }
  function reviews() {
    if (!data) return;
    const kind=$('review-kind').value, matches=selected.filter(i=>reviewMatches(i,kind));
    $('review-count').textContent='Mostrando '+Math.min(reviewLimit,matches.length)+' de '+matches.length+' fichas · Filtros actuales';
    const detail=i=>kind==='metadata' || kind.startsWith('gap:') ? i.metadata_gaps.map(g=>gaps[g]).join(' · ') : kind==='versions'?comparisons[i.version_comparison]:kind==='media'?'Recurso y ficha declaran versiones diferentes':kind==='unverified'?'Registrar la versión de origen de '+i.unverified_asset_ids.length+' recursos':kind==='no-video'?'Sin vídeo publicado; no es una incidencia técnica':editorial[i.editorial_status];
    $('review-records').replaceChildren(...(matches.length?matches.slice(0,reviewLimit).map(i=>record(i,detail(i))):[node('div',{class:'workspace-empty'},node('strong',{},'No hay fichas en esta selección'),paragraph('Puedes cambiar la cola o ajustar los filtros. Esto no certifica revisiones no registradas.'))]));
    $('review-more').hidden=matches.length<=reviewLimit;
    $('review-quick-queues').replaceChildren(...[['pending','Revisión editorial'],['metadata','Datos de control'],['unverified','Vigencia no evaluable'],['no-video','Cobertura de vídeo']].map(([value,label])=>button(label,{'data-queue':value,'aria-pressed':String(kind===value)})));
  }
  function publication() {
    if (!data) return;
    const s=C.summarize(selected), fresh=freshness();
    $('publication-summary').replaceChildren(metric(s.total,'Fichas seleccionadas','Publicadas en esta versión'),metric(s.pending,'Pendientes','Revisión editorial','amber'),metric(s.approved,'Aprobadas','Aprobación explícita','teal'),metric(s.unspecified,'Sin estado','Sin aprobación inferida','slate'));
    $('publication-count').textContent='Mostrando '+Math.min(publicationLimit,selected.length)+' de '+selected.length+' fichas seleccionadas';
    $('publication-build').replaceChildren(document.createTextNode('Versión publicada: '),publicLink(data.revision_url,(data.revision || '').slice(0,7) || 'No identificada'),document.createTextNode(' · Catálogo generado: '+dateLabel(data.generated_at)));
    $('publication-freshness').replaceChildren(node('span',{class:'workspace-tag','data-tone':fresh.current?'good':'neutral'},fresh.label),paragraph(report?'Última comprobación registrada: '+dateLabel(report.generated_at)+'. La vigencia requiere la misma versión del sitio y un informe de hasta 36 horas.':'Todavía no hay un informe técnico disponible para esta consulta.'));
    $('publication-records').replaceChildren(...(selected.length?selected.slice(0,publicationLimit).map(i=>record(i,'Versión de ficha: '+(i.content_version ?? 'sin registrar'),true)):[paragraph('No hay fichas para estos filtros.')]));
    $('publication-more').hidden=selected.length<=publicationLimit;
  }
  function impact() {
    if (!data) return;
    const source=$('impact-source').value, matches=affectedBy(selected,source,$('impact-section').value);
    $('impact-count').textContent=source?'Mostrando '+Math.min(impactLimit,matches.length)+' de '+matches.length+' fichas relacionadas dentro de los filtros actuales.':'Selecciona una fuente para seguir sus conexiones.';
    $('impact-records').replaceChildren(...matches.slice(0,impactLimit).map(i=>record(i,i.embedded_count+' ubicaciones multimedia · '+i.marketing_codes.length+' piezas relacionadas')));
    $('impact-more').hidden=matches.length<=impactLimit;
    $('impact-export').disabled=!source || !matches.length;
  }
  function impactSections(value=$('impact-section').value) {
    const source=$('impact-source').value;
    const sections=[...new Set(affectedBy(selected,source).flatMap(i=>i.source.sections))].sort();
    choices($('impact-section'),sections.map(s=>[s,s]),'Todas sus referencias');
    $('impact-section').value=sections.includes(value)?value:'';
    $('impact-section').disabled=!source;
  }
  function filterHierarchy() {
    const f=filters(), active=Object.values(f).some(Boolean), tree=$('maintenance-structure');
    if (active && !snapshot) snapshot=new Map([...tree.querySelectorAll('details')].map(d=>[d,d.open]));
    const codes=new Set(selected.map(i=>i.code));
    tree.querySelectorAll('[data-maint-topic]').forEach(a=>{a.closest('li').hidden=!codes.has(a.dataset.maintTopic);});
    ['[data-maint-section]','[data-maint-role]'].forEach(selector=>tree.querySelectorAll(selector).forEach(d=>{d.hidden=![...d.querySelectorAll('[data-maint-topic]')].some(a=>!a.closest('li').hidden);if(active&&!d.hidden)d.open=true;}));
    tree.querySelectorAll('[data-maint-category]').forEach(d=>{const roles=[...d.querySelectorAll('[data-maint-role]')];d.hidden=roles.length?!roles.some(r=>!r.hidden):Boolean((f.category&&d.dataset.maintCategory!==f.category)||f.query||f.role||f.section);if(active&&!d.hidden)d.open=true;});
    if (!active&&snapshot) {snapshot.forEach((open,d)=>{d.open=open;});snapshot=null;}
  }
  function refresh(syncURL=true) {
    if (!data) return;
    selected=filterItems(data.items,filters());
    $('control-count').textContent=selected.length+' de '+data.items.length+' fichas';
    const active=Object.values(filters()).filter(Boolean).length;
    $('filter-active-count').textContent=active?'· '+active+' activos':'';
    choices($('impact-source'),[...new Set(selected.map(i=>i.source.label).filter(Boolean))].sort().map(v=>[v,v]),'Elige una fuente');
    impactSections();
    filterHierarchy(); overview(); reviews(); publication(); impact();
    if(syncURL)writeURL(); showView();
  }
  function openControl(code,focus=true,trigger=null) {
    const i=data?.items.find(item=>item.code===code);if(!i)return;
    if(focus){opener=trigger || document.activeElement;originScroll=window.scrollY;}
    openCode=code;
    const dl=node('dl'), source=i.source;
    [['Ubicación',[i.category,i.role,i.stage].join(' → ')],['Fuente funcional',source.label || 'Sin registrar'],['Sección',source.sections.join('; ') || 'Sin identificar'],['Versión de guía',source.version_identified?source.version:'Sin identificar'],['Versión de ficha',i.content_version ?? 'Sin registrar'],['Preparación',comparisons[i.version_comparison]],['Revisión registrada',i.reviewed_at || 'Sin fecha registrada'],['Recursos',i.embedded_count+' ubicaciones en ficha · '+i.distribution_count+' publicaciones externas'],['Piezas relacionadas',i.marketing_codes.join(', ') || 'Sin correspondencia registrada']].forEach(([label,value])=>dl.append(node('dt',{},label),node('dd',{},value)));
    const control=data.editorial_controls.find(c=>c.category_id===i.category_id);
    $('topic-control').replaceChildren(node('div',{class:'drawer-topline'},node('span',{class:'panel-kicker'},'CONTROL DE FICHA'),button('Cerrar ✕',{'data-close-control':'','aria-label':'Cerrar control de ficha'})),node('span',{class:'record-code'},i.code),node('h2',{id:'topic-control-title',tabindex:'-1'},i.title),tags(i),node('div',{class:'drawer-section'},node('h3',{},'Información y trazabilidad'),dl),node('div',{class:'drawer-section'},node('h3',{},'Siguientes acciones'),...(i.metadata_gaps || []).map(g=>node('p',{class:'drawer-task'},node('span',{'aria-hidden':'true'},'→'),gaps[g])),i.unverified_asset_ids?.length?paragraph(i.unverified_asset_ids.length+' recursos necesitan versión de origen para contrastar su vigencia.'):null),node('div',{class:'topic-control-actions'},publicLink(i.canonical_url,'Abrir ficha publicada →'),publicLink(i.source_file_url,'Ver fuente publicada →'),publicLink(control?.url,'Consultar revisión editorial →'),publicLink(i.preparation?.reference_url,'Consultar preparación →'),button('Consultar multimedia vinculada',{'data-show-media':code})),paragraph('Consulta pública. Estas acciones no editan, aprueban ni sincronizan documentos privados.'));
    $('topic-control').hidden=false;
    if(!$('topic-control').open)$('topic-control').showModal();
    if(focus)$('topic-control-title').focus();
    writeURL();
  }
  function closeControl() {
    const dialog=$('topic-control');
    if(dialog.open)dialog.close();dialog.hidden=true;openCode=null;writeURL();
    if(opener?.isConnected){opener.focus({preventScroll:true});window.scrollTo(0,originScroll);}
  }
  $('topic-control').addEventListener('cancel',event=>{event.preventDefault();closeControl();});
  root.addEventListener('click',event=>{
    const control=event.target.closest('[data-open-control]');if(control)openControl(control.dataset.openControl,true,control);
    if(event.target.closest('[data-close-control]'))closeControl();
    const queue=event.target.closest('[data-queue]');if(queue){$('review-kind').value=queue.dataset.queue;reviewLimit=20;reviews();writeURL();navigate('m-revisiones');}
    const go=event.target.closest('[data-go-view]');if(go)navigate(go.dataset.goView);
    const media=event.target.closest('[data-show-media]');if(media){const code=media.dataset.showMedia;closeControl();navigate('m-multimedia');window.dispatchEvent(new CustomEvent('maintenance:topic',{detail:{code}}));}
  });
  Object.entries(fields).forEach(([key,id])=>$(id).addEventListener(key==='query'?'input':'change',()=>{if(key==='category'||key==='role')dependentFilters();reviewLimit=publicationLimit=impactLimit=20;refresh();}));
  $('control-clear').addEventListener('click',()=>{Object.values(fields).forEach(id=>{$(id).value='';});dependentFilters();reviewLimit=publicationLimit=impactLimit=20;refresh();$('control-query').focus();});
  $('review-kind').addEventListener('change',()=>{reviewLimit=20;reviews();writeURL();});
  $('review-more').addEventListener('click',()=>{reviewLimit+=20;reviews();});
  $('publication-more').addEventListener('click',()=>{publicationLimit+=20;publication();});
  $('impact-more').addEventListener('click',()=>{impactLimit+=20;impact();});
  $('impact-source').addEventListener('change',()=>{impactSections('');impactLimit=20;impact();writeURL();});
  $('impact-section').addEventListener('change',()=>{impactLimit=20;impact();writeURL();});
  $('impact-export').addEventListener('click',()=>{const rows=affectedBy(selected,$('impact-source').value,$('impact-section').value);C.download([['Código','Título','Fuente','Secciones','Recursos en ficha','Piezas relacionadas','URL'],...rows.map(i=>[i.code,i.title,i.source.label,i.source.sections.join(' | '),i.embedded_count,i.marketing_codes.join(' | '),i.canonical_url])],'mantenimiento-impacto.csv');});
  $('workspace-copy').addEventListener('click',async()=>{$('workspace-feedback').textContent=await C.copy(location.href)?'Vista copiada. Incluye los filtros y la selección actuales.':'No se pudo copiar. Puedes usar la dirección de esta página.';});
  $('workspace-export').addEventListener('click',()=>{
    if(!data)return;
    if(activeView==='m-multimedia'){window.dispatchEvent(new Event('maintenance:export'));return;}
    const rows=activeView==='m-revisiones'?selected.filter(i=>reviewMatches(i,$('review-kind').value)):selected;
    C.download([['Código','Título','Categoría','Rol','Sección','Estado editorial','Versión de ficha','Fuente','Datos pendientes','URL'],...rows.map(i=>[i.code,i.title,i.category,i.role,i.stage,editorial[i.editorial_status],i.content_version,i.source.label,i.metadata_gaps.map(g=>gaps[g]).join(' | '),i.canonical_url])],'mantenimiento-'+activeView.slice(2)+'.csv');
    $('workspace-feedback').textContent='Exportadas '+rows.length+' fichas de la selección completa.';
  });
  function reportChanged() {report=window.__maintenanceData || null;if(data){publication();if(openCode){const item=data.items.find(i=>i.code===openCode);if(item)$('topic-control').querySelector('.workspace-tags')?.replaceWith(tags(item));}}}
  window.addEventListener('maintenance:report',reportChanged);
  window.addEventListener('keydown',event=>{if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k'&&!$('topic-control').open){event.preventDefault();$('control-query').focus();}});
  async function load(reload=false) {
    $('workspace-load-status').textContent='Actualizando datos publicados…';
    try {
      const result=await C.load(root.dataset.controlUrl,reload);
      if(result.schema_version!==1||!Array.isArray(result.items)||!Array.isArray(result.categories))throw new Error('Formato de control no válido');
      data=result;
      const saved=new URL(location.href).searchParams;
      choices($('control-category'),data.categories.map(c=>[c.id,c.name]),'Todas las categorías');
      if(!reload){$('control-category').value=saved.get('category') || '';dependentFilters();$('control-role').value=saved.get('role') || '';dependentFilters();$('control-section').value=saved.get('section') || ''; $('control-query').value=(saved.get('query') || '').slice(0,160);const queue=saved.get('queue');if([...$('review-kind').options].some(o=>o.value===queue))$('review-kind').value=queue;}
      else dependentFilters();
      $('workspace-filters').hidden=false;$('workspace-copy').disabled=false;$('workspace-export').disabled=false;
      $('workspace-load-status').textContent='Catálogo de '+data.items.length+' fichas · Actualizado '+dateLabel(data.generated_at);
      $('maintenance-structure').querySelectorAll('[data-maint-topic]').forEach(a=>{if(!a.closest('li').querySelector('.control-topic-button')){const b=button('Ver control →',{'data-open-control':a.dataset.maintTopic,'aria-label':'Ver control: '+a.textContent.trim()});b.classList.add('control-topic-button');a.closest('li').append(b);}});
      $('editorial-control-links').replaceChildren(...data.editorial_controls.map(c=>node('p',{class:'maint-meta'},publicLink(c.url,c.title+' →'))));
      const changes=data.guide_changes.map(change=>node('article',{class:'workspace-record'},
        node('div',{},node('h4',{},change.title),paragraph(change.source_label+' · '+change.affected_codes.length+' fichas · '+dateLabel(change.recorded_at))),
        publicLink(change.reference_url,'Consultar cambio →')));
      $('guide-change-records').replaceChildren(...(changes.length?changes:[paragraph('Sin cambios registrados en este panel. No se ha comprobado que la guía permanezca sin cambios.')]));
      refresh(false);
      if(saved.get('source')){$('impact-source').value=saved.get('source');impactSections(saved.get('sourceSection') || '');impact();}
      reportChanged();
      const topic=saved.get('topic');if(topic)openControl(topic);
    } catch(error) {
      $('workspace-load-status').textContent='No se pudo cargar el control: '+error.message+'. '+(data?'Se conservan los datos anteriores.':'La jerarquía y las consultas independientes siguen disponibles.');
      if(!data){$('overview-metrics').replaceChildren(paragraph('Panorama sin datos disponibles. Usa Recargar datos para volver a intentarlo.'));$('review-records').textContent='Colas de revisión sin datos disponibles.';$('publication-build').textContent='No se puede determinar la versión desde el control.';}
    }
  }
  $('workspace-reload').addEventListener('click',()=>{load(true);window.dispatchEvent(new Event('maintenance:reload'));});
  const filterDetails=root.querySelector('.workspace-filter-details');filterDetails.open=false;
  C.load(root.dataset.shareUrl).then(value=>{sharedItems=value.items || [];sharedReady=true;if(data)overview();}).catch(()=>{});
  window.addEventListener('maintenance:shared',event=>{sharedItems=event.detail.items || [];sharedReady=true;if(data)overview();});
  window.addEventListener('popstate',()=>{
    if(!data)return;
    const saved=new URL(location.href).searchParams;
    window.dispatchEvent(new Event('maintenance:restore'));
    $('control-category').value=saved.get('category') || '';dependentFilters();
    $('control-role').value=saved.get('role') || '';dependentFilters();
    $('control-section').value=saved.get('section') || '';$('control-query').value=(saved.get('query') || '').slice(0,160);
    const queue=saved.get('queue') || 'pending';if([...$('review-kind').options].some(o=>o.value===queue))$('review-kind').value=queue;
    reviewLimit=publicationLimit=impactLimit=20;refresh(false);
    $('impact-source').value=saved.get('source') || '';impactSections(saved.get('sourceSection') || '');impact();
    const topic=saved.get('topic');
    if(topic)openControl(topic);else if($('topic-control').open){$('topic-control').close();$('topic-control').hidden=true;openCode=null;}
  });
  load();
})();
