/* Public, read-only control views. All variable text is rendered as DOM text. */
(() => {
  'use strict';
  const norm = v => String(v ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
  const editorial = {approved:'Aprobada explícitamente',pending_review:'Pendiente de revisión',draft:'Borrador',changes_requested:'Cambios solicitados',unspecified:'Sin estado explícito'};
  const comparisons = {no_reference:'Sin referencia en preparación registrada',same_content:'Mismo contenido según la huella registrada',different_content:'Contenido distinto según la huella registrada',same_version_unverified:'Mismo número de versión; contenido sin contrastar',different_version:'Versiones declaradas diferentes',unverified:'Sin datos suficientes para comparar'};
  const gaps = {editorial_state:'Estado editorial sin registrar',functional_source:'Fuente funcional sin registrar',source_section:'Sección de fuente sin identificar',guide_version:'Versión de guía sin identificar',content_version:'Versión de ficha sin registrar'};
  function filterItems(items,f={}) {
    const words = norm(f.query).split(/\s+/).filter(Boolean);
    return items.filter(i => (!f.category || i.category_id===f.category) && (!f.role || i.role_id===f.role) && (!f.section || i.stage_url===f.section) && words.every(w => norm([i.code,i.title,i.category,i.role,i.stage,i.source?.reference].join(' ')).includes(w)));
  }
  function affectedBy(items,source,section='') { return source ? items.filter(i => i.source?.label===source && (!section || i.source.sections.includes(section))) : []; }
  function reviewMatches(i,kind) {
    if(kind==='pending') return ['pending_review','changes_requested'].includes(i.editorial_status);
    if(kind==='unspecified') return i.editorial_status==='unspecified';
    if(kind==='metadata') return Boolean(i.metadata_gaps?.length);
    if(kind==='versions') return ['different_content','different_version'].includes(i.version_comparison);
    if(kind==='media') return Boolean(i.stale_asset_ids?.length);
    return false;
  }
  const technicalLabel = r => ({OK:'Correcto',REVISAR:'Requiere revisión técnica',ROTO:'Con incidencias','SIN COMPROBAR':'Sin comprobar'})[r?.status] || 'Sin comprobar';
  if(typeof module!=='undefined' && module.exports) module.exports={norm,filterItems,affectedBy,reviewMatches,technicalLabel};
  if(typeof document==='undefined') return;
  const $=id=>document.getElementById(id), root=$('maintenance-workspace');
  if(!root) return;
  function node(tag,attrs={},...children) {
    const n=document.createElement(tag);
    for(const [key,value] of Object.entries(attrs)) n.setAttribute(key,String(value));
    for(const child of children.flat()) if(child!==null && child!==undefined) n.append(child instanceof Node ? child : document.createTextNode(String(child)));
    return n;
  }
  const paragraph=text=>node('p',{class:'maint-meta'},text);
  const button=(text,attrs={})=>node('button',{type:'button',class:'workspace-button',...attrs},text);
  function publicLink(value,label) {
    if(!value) return null;
    try {
      const target=new URL(value,location.href);
      if(target.protocol!=='https:' && !(target.protocol==='http:' && target.origin===location.origin)) return null;
      return node('a',{href:target.href,target:'_blank',rel:'noopener noreferrer'},label);
    } catch(_) { return null; }
  }
  const dateLabel=v=>v && !Number.isNaN(new Date(v).getTime()) ? new Date(v).toLocaleString('es-ES') : 'Sin fecha registrada';
  const published=i=>i.publication_status==='test_published' ? 'Publicada para pruebas' : 'Publicada';
  let data=null, selected=[], tech=new Map(), technicalDate='', openCode=null, snapshot=null;
  let reviewLimit=20, publicationLimit=20, activeView='m-contenido';
  const panels=[...root.querySelectorAll('[data-maint-view]')], nav=[...root.querySelectorAll('[data-maint-view-link]')];
  const fields=['control-query','control-category','control-role','control-section'];
  const filters=()=>({query:$('control-query').value,category:$('control-category').value,role:$('control-role').value,section:$('control-section').value});
  function choices(select,rows,label) {
    const previous=select.value;
    select.replaceChildren(new Option(label,''));
    rows.forEach(([value,title])=>select.add(new Option(title,value)));
    if(rows.some(([value])=>value===previous)) select.value=previous;
  }
  function dependentFilters() {
    if(!data) return;
    const category=$('control-category').value;
    const roles=new Map(data.categories.filter(c=>!category || c.id===category).flatMap(c=>c.roles.map(r=>[r.id,r.name])));
    choices($('control-role'),[...roles],'Todos los roles'); $('control-role').disabled=!roles.size;
    const entries=filterItems(data.items,{category,role:$('control-role').value});
    const sections=new Map(entries.map(i=>[i.stage_url,i.role+' · '+i.stage]));
    choices($('control-section'),[...sections],'Todas las secciones'); $('control-section').disabled=!sections.size;
  }
  function showView() {
    const aliases={'maintenance-search':'m-multimedia','maintenance-dashboard':'m-publicacion','maintenance-structure':'m-contenido','topic-control':'m-contenido'};
    const hash=location.hash.slice(1);
    activeView=panels.some(p=>p.id===hash) ? hash : (aliases[hash] || 'm-contenido');
    panels.forEach(p=>{p.hidden=p.id!==activeView;});
    nav.forEach(a=>{if(a.dataset.maintViewLink===activeView) a.setAttribute('aria-current','true'); else a.removeAttribute('aria-current');});
    $('workspace-filters').hidden=!data || activeView==='m-multimedia';
  }
  function navigate(view) { location.hash=view; showView(); }
  window.addEventListener('hashchange',showView); showView();
  function tags(i) {
    return node('div',{class:'workspace-tags'},[['Editorial',editorial[i.editorial_status] || editorial.unspecified],['Publicación',published(i)],['Técnico',technicalLabel(tech.get(i.code))]].map(([label,value])=>node('span',{class:'workspace-tag'},node('strong',{},label+': '),value)));
  }
  function openControl(code,focus=true) {
    const i=data?.items.find(item=>item.code===code); if(!i) return;
    openCode=code;
    const source=i.source, prep=i.preparation, dl=node('dl');
    const rows=[['Código canónico',i.code],['Ubicación',[i.category,i.role,i.stage].join(' → ')],['Fuente funcional',source.label || 'Sin registrar'],['Sección de la fuente',source.sections.join('; ') || 'Sin identificar'],['Versión de la guía',source.version || 'Sin identificar'],['Versión en esta publicación',i.content_version ?? 'Sin registrar'],['Versión en preparación',prep?.version ?? 'Sin referencia registrada'],['Comparación',comparisons[i.version_comparison]],['Revisión registrada',i.reviewed_at || 'Sin fecha; no se deduce aprobación'],['Documento editorial','No vinculado en este catálogo público'],['Recursos vinculados',i.embedded_count+' dentro de ficha · '+i.distribution_count+' publicaciones externas'],['Piezas publicitarias',i.marketing_codes.join(', ') || 'Sin correspondencia verificada']];
    rows.forEach(([label,value])=>dl.append(node('dt',{},label),node('dd',{},value)));
    const warning=(i.metadata_gaps.length ? 'Datos pendientes: '+i.metadata_gaps.map(g=>gaps[g]).join(' · ')+'. ' : '')+'Sin referencia de trabajo no se puede confirmar sincronización con Drive ni ausencia de borradores privados.';
    $('topic-control').replaceChildren(node('div',{class:'topic-control-heading'},node('h3',{id:'topic-control-title',tabindex:'-1'},i.title),button('Cerrar control',{'data-close-control':''})),tags(i),dl,node('p',{class:'control-warning'},warning),node('div',{class:'topic-control-actions'},publicLink(i.canonical_url,'Abrir ficha publicada'),publicLink(i.source_file_url,'Ver archivo de esta versión'),publicLink(prep?.reference_url,'Consultar preparación'),button('Consultar multimedia vinculada',{'data-show-media':code})));
    $('topic-control').hidden=false;
    if(focus) { navigate('m-contenido'); $('topic-control-title').focus(); $('topic-control').scrollIntoView({block:'start'}); }
  }
  function filterHierarchy() {
    const f=filters(), active=Boolean(f.query.trim() || f.category || f.role || f.section), tree=$('maintenance-structure');
    if(active && !snapshot) snapshot=new Map([...tree.querySelectorAll('details')].map(d=>[d,d.open]));
    const codes=new Set(selected.map(i=>i.code));
    tree.querySelectorAll('[data-maint-topic]').forEach(a=>{a.closest('li').hidden=!codes.has(a.dataset.maintTopic);});
    for(const selector of ['[data-maint-section]','[data-maint-role]']) tree.querySelectorAll(selector).forEach(d=>{d.hidden=![...d.querySelectorAll('[data-maint-topic]')].some(a=>!a.closest('li').hidden); if(active && !d.hidden) d.open=true;});
    tree.querySelectorAll('[data-maint-category]').forEach(d=>{const roles=[...d.querySelectorAll('[data-maint-role]')]; d.hidden=roles.length ? !roles.some(r=>!r.hidden) : Boolean((f.category && d.dataset.maintCategory!==f.category) || f.query.trim() || f.role || f.section); if(active && !d.hidden) d.open=true;});
    if(!active && snapshot) {snapshot.forEach((open,d)=>{d.open=open;}); snapshot=null;}
  }
  function record(i,detail,withTags=false) {
    return node('article',{class:'workspace-record','data-control-record':i.code},node('div',{},node('h3',{},i.title),paragraph(i.code+' · '+i.role+' · '+i.stage),detail ? paragraph(detail) : null,withTags ? tags(i) : null),button('Ver control',{'data-open-control':i.code}));
  }
  function reviews() {
    if(!data) return;
    const kind=$('review-kind').value, matches=selected.filter(i=>reviewMatches(i,kind));
    $('review-count').textContent=matches.length+' fichas en esta cola con los filtros actuales. No se modifica su estado.';
    const detail=i=>kind==='metadata' ? i.metadata_gaps.map(g=>gaps[g]).join(' · ') : kind==='versions' ? comparisons[i.version_comparison] : kind==='media' ? 'Versiones derivadas: '+i.stale_asset_ids.join(', ') : editorial[i.editorial_status];
    $('review-records').replaceChildren(...(matches.length ? matches.slice(0,reviewLimit).map(i=>record(i,detail(i))) : [paragraph('No hay coincidencias en esta cola; no certifica otras revisiones ni registros privados.')]));
    $('review-more').hidden=matches.length<=reviewLimit;
  }
  function publication() {
    if(!data) return;
    const s=data.summary, counts=[[s.published,'Fichas en esta publicación'],[s.editorial.pending_review || 0,'Pendientes de revisión'],[s.editorial.approved || 0,'Aprobadas explícitamente'],[s.editorial.unspecified || 0,'Sin estado editorial explícito']];
    $('publication-summary').replaceChildren(...counts.map(([count,label])=>node('div',{},node('strong',{},count),node('span',{},label))));
    $('publication-build').replaceChildren(document.createTextNode('Compilación: '+dateLabel(data.generated_at)+'. '));
    const ref=publicLink(data.revision_url,'Ver versión del sitio '+(data.revision || '').slice(0,7)); if(ref) $('publication-build').append(ref);
    $('publication-build').append(document.createTextNode('. Última comprobación técnica: '+(technicalDate ? dateLabel(technicalDate) : 'sin reporte disponible')+'. No comprueba sincronización con Drive.'));
    $('publication-records').replaceChildren(...(selected.length ? selected.slice(0,publicationLimit).map(i=>record(i,'Versión '+(i.content_version ?? 'sin registrar'),true)) : [paragraph('No hay fichas publicadas para estos filtros.')]));
    $('publication-more').hidden=selected.length<=publicationLimit;
  }
  function impact() {
    if(!data) return;
    const source=$('impact-source').value, matches=affectedBy(data.items,source,$('impact-section').value);
    $('impact-count').textContent=source ? matches.length+' fichas relacionadas. Revisa también referencias sin sección identificada.' : 'Elige una fuente para consultar sus relaciones.';
    $('impact-records').replaceChildren(...matches.map(i=>record(i,i.embedded_count+' recursos en ficha · '+i.distribution_count+' publicaciones externas · '+i.marketing_codes.length+' piezas verificadas')));
  }
  function refresh() {if(!data) return; selected=filterItems(data.items,filters()); $('control-count').textContent=selected.length+' de '+data.items.length+' fichas coinciden. Filtros para contenido, revisiones y publicación.'; filterHierarchy(); reviews(); publication();}
  function reportReady() {
    const report=window.__maintenanceData; if(!report || !Array.isArray(report.items)) return false;
    tech=new Map(report.items.map(i=>[i.code,i])); technicalDate=report.generated_at || '';
    const pending=$('maintenance-dashboard').querySelector('.maint-pending'); if(pending) $('marketing-unlinked').replaceChildren(pending);
    publication(); if(openCode) openControl(openCode,false); return true;
  }
  const observer=new MutationObserver(()=>{if(reportReady()) observer.disconnect(); else if($('maintenance-dashboard').textContent.includes('No se pudo cargar')) {$('marketing-unlinked').textContent='Inventario no disponible: no se pudo cargar el reporte técnico.'; observer.disconnect();}});
  observer.observe($('maintenance-dashboard'),{childList:true}); if(reportReady()) observer.disconnect();
  root.addEventListener('click',event=>{
    const open=event.target.closest('[data-open-control]'); if(open) openControl(open.dataset.openControl);
    if(event.target.closest('[data-close-control]')) {const code=openCode; $('topic-control').hidden=true; openCode=null; const b=[...root.querySelectorAll('.control-topic-button')].find(n=>n.dataset.openControl===code); if(b && b.offsetParent) b.focus();}
    const media=event.target.closest('[data-show-media]'); if(media) {navigate('m-multimedia'); $('maint-search-clear').click(); $('maint-search-text').value=media.dataset.showMedia; $('maint-search-text').dispatchEvent(new Event('input',{bubbles:true})); $('maint-search-text').focus();}
  });
  fields.forEach(id=>$(id).addEventListener(id==='control-query' ? 'input' : 'change',()=>{if(id==='control-category' || id==='control-role') dependentFilters(); reviewLimit=publicationLimit=20; refresh();}));
  $('control-clear').addEventListener('click',()=>{fields.forEach(id=>{$(id).value='';}); dependentFilters(); reviewLimit=publicationLimit=20; refresh(); $('control-query').focus();});
  $('review-kind').addEventListener('change',()=>{reviewLimit=20; reviews();});
  $('review-more').addEventListener('click',()=>{reviewLimit+=20; reviews();});
  $('publication-more').addEventListener('click',()=>{publicationLimit+=20; publication();});
  $('impact-source').addEventListener('change',()=>{if(!data) return; const sections=[...new Set(affectedBy(data.items,$('impact-source').value).flatMap(i=>i.source.sections))].sort((a,b)=>a.localeCompare(b,'es')); choices($('impact-section'),sections.map(s=>[s,s]),'Todas las referencias de esta fuente'); $('impact-section').value=''; $('impact-section').disabled=!$('impact-source').value; impact();});
  $('impact-section').addEventListener('change',impact);
  fetch(root.dataset.controlUrl,{cache:'no-store'}).then(r=>{if(!r.ok) throw new Error('HTTP '+r.status); return r.json();}).then(result=>{
    if(result.schema_version!==1 || !Array.isArray(result.items) || !Array.isArray(result.categories)) throw new Error('Formato de control no válido');
    data=result;
    $('workspace-load-status').textContent='Control de metadatos públicos. Los datos ausentes no se consideran aprobados ni sincronizados.';
    choices($('control-category'),data.categories.map(c=>[c.id,c.name]),'Todas las categorías'); dependentFilters();
    $('maintenance-structure').querySelectorAll('[data-maint-topic]').forEach(a=>{if(data.items.some(i=>i.code===a.dataset.maintTopic)) {const b=button('Ver control',{'data-open-control':a.dataset.maintTopic,'aria-label':'Ver control: '+a.textContent.trim()}); b.classList.add('control-topic-button'); a.closest('li').append(b);}});
    const phases={classified:'Clasificada',organized:'Organizada',identified:'Identificada',developed:'Desarrollada'};
    $('preparation-records').replaceChildren(...(data.preparation.length ? data.preparation.map(p=>node('article',{class:'workspace-record'},node('div',{},node('h3',{},p.title || p.code),paragraph(p.code+' · '+phases[p.phase]+' · No publicada'),publicLink(p.reference_url,'Consultar referencia')))) : [paragraph('No hay metadatos públicos de nuevas fichas en preparación registrados. No afirma que no existan borradores en Drive.')]));
    $('editorial-control-links').replaceChildren(...data.editorial_controls.map(c=>node('p',{class:'maint-meta'},publicLink(c.url,c.title),' · Consulta el estado en el control original; no se modifica ni se sincroniza automáticamente.')));
    $('guide-change-records').replaceChildren(...(data.guide_changes.length ? data.guide_changes.map(c=>node('article',{class:'workspace-record'},node('div',{},node('h3',{},c.title),paragraph(c.source_label+' · '+c.affected_codes.length+' fichas relacionadas · '+(c.recorded_at || 'Sin fecha')),publicLink(c.reference_url,'Consultar cambio registrado')))) : [paragraph('No hay cambios de guía registrados en este panel. No equivale a comprobar que la guía no haya cambiado.')]));
    const sources=[...new Set(data.items.map(i=>i.source.label).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'es')); choices($('impact-source'),sources.map(s=>[s,s]),'Elige una fuente');
    refresh(); impact(); showView();
  }).catch(error=>{$('workspace-load-status').textContent='No se pudo cargar el control: '+error.message+'. La jerarquía y las otras consultas siguen disponibles.'; $('review-records').textContent='Colas de revisión sin datos disponibles.'; $('guide-change-records').textContent='Registros de cambio no disponibles.'; $('publication-build').textContent='No se puede determinar la versión de esta publicación desde el control.';});
})();
