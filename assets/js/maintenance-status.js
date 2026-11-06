/* Category -> role -> section -> topic. Does not change editorial or publication states. */
(() => {
  'use strict';
  function groupItems(items, categories, baseurl = '') {
    const groups = new Map();
    for (const item of items || []) {
      let path;
      try { path = new URL(item.canonical_url || '/', 'https://local.invalid').pathname; } catch (_) { path = '/'; }
      if (baseurl && path.startsWith(baseurl + '/')) path = path.slice(baseurl.length);
      const category = categories.find(c => path.startsWith(c.url));
      const role = category?.roles?.find(r => path.startsWith(r.url));
      const categoryId = category?.id || 'unknown:' + (item.category || '');
      const roleId = role?.id || 'unknown:' + (item.role || '');
      if (!groups.has(categoryId)) groups.set(categoryId, {
        id: categoryId, name: category?.name || item.category || 'Sin categoría identificada',
        order: category ? categories.indexOf(category) : categories.length, roles: new Map()
      });
      const cat = groups.get(categoryId);
      if (!cat.roles.has(roleId)) cat.roles.set(roleId, {
        id: roleId, name: role?.name || item.role || 'Sin rol identificado',
        order: role ? category.roles.indexOf(role) : 999, sections: new Map()
      });
      const rg = cat.roles.get(roleId);
      const sectionId = item.stage_url || JSON.stringify([item.stage_order ?? 999, item.stage || 'Sin sección']);
      if (!rg.sections.has(sectionId)) rg.sections.set(sectionId, {
        id: sectionId, name: item.stage || 'Sin sección', order: Number(item.stage_order ?? 999), items: []
      });
      rg.sections.get(sectionId).items.push(item);
    }
    return [...groups.values()].sort((a, b) => a.order - b.order).map(cat => ({...cat,
      roles: [...cat.roles.values()].sort((a, b) => a.order - b.order).map(role => ({...role,
        sections: [...role.sections.values()].sort((a, b) => a.order - b.order || a.id.localeCompare(b.id))
      }))
    }));
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {groupItems};
  if (typeof document === 'undefined') return;
  const root = document.getElementById('maintenance-dashboard');
  if (!root) return;
  const C=window.MaintenanceCore, el=C.node;
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  const base=root.dataset.baseurl || '';
  const socialProviders=new Set(['youtube','facebook','instagram','tiktok','x','linkedin']);
  const names={youtube:'YouTube',facebook:'Facebook',instagram:'Instagram',tiktok:'TikTok',x:'X',linkedin:'LinkedIn'};
  const safeUrl=value=>{
    const path=String(value || '');
    return C.safeURL(base && /^\/(?!\/)/.test(path) && !path.startsWith(base+'/') ? base+path : path,location.href);
  };
  let report=null, revision=null, selected=null, failed=false, lazy=new Map();
  const freshness=()=>failed?{current:false,label:'Actualización no disponible · datos anteriores'}:C.reportState(report,revision);
  function badge(status){const fresh=freshness(),label=fresh.current?(status || 'SIN COMPROBAR'):(status?'Anterior: '+status:'Sin comprobar');return '<span class="maint-status" data-status="'+esc(fresh.current?status:'SIN COMPROBAR')+'">'+esc(label)+'</span>';}
  function renderResource(resource) {
    const url = safeUrl(resource.url || resource.src);
    const provider = resource.storage === 'internal' ? (resource.type || 'Recurso propio') : (names[String(resource.provider || '').toLowerCase()] || resource.provider || resource.type || 'Recurso externo');
    return `<div class="maint-resource"><div class="maint-resource-head"><div>
      <div class="maint-resource-name">${esc(provider)} · ${esc(resource.id || 'Sin ID')}</div>
      ${resource.title ? `<div class="maint-resource-meta">${esc(resource.title)}</div>` : ''}
      ${resource.video_id ? `<div class="maint-resource-meta">Video ID: ${esc(resource.video_id)}</div>` : ''}
      <div class="maint-resource-meta">Versión recurso / derivada: ${esc(resource.version ?? '—')} / ${esc(resource.derived_from_version ?? '—')}</div>
      ${resource.detail ? `<div class="maint-resource-meta">${esc(resource.detail)}</div>` : ''}
      </div>${badge(resource.status)}</div>
      ${url ? `<div class="maint-resource-actions"><a href="${esc(url)}" target="_blank" rel="noopener noreferrer">Abrir recurso</a></div>` : ''}</div>`;
  }
  function resourceGroup(title, resources, empty) {
    return `<div class="maint-layer-group"><div class="maint-layer-group-title">${esc(title)}</div>${resources.length ? resources.map(renderResource).join('') : `<div class="maint-empty">${esc(empty)}</div>`}</div>`;
  }
  function renderFicha(item) {
    const media = item.media || [];
    const own = media.filter(r => r.storage === 'internal');
    const social = media.filter(r => socialProviders.has(String(r.provider || '').toLowerCase()));
    const other = media.filter(r => r.storage !== 'internal' && !socialProviders.has(String(r.provider || '').toLowerCase()));
    const issues = (item.checks || []).filter(c => c.status !== 'OK');
    const url = safeUrl(item.canonical_url);
    return `<article class="maint-ficha" data-technical-topic="${esc(item.code)}">
      <div class="maint-ficha-head"><div><div class="maint-ficha-title">${esc(item.title)}</div>
      <div class="maint-code">${esc(item.code)}</div>
      <div class="maint-meta">Versión canónica: ${esc(item.content_version ?? 'sin definir')} · Revisión registrada: ${esc(item.reviewed || 'sin fecha')}</div>
      ${url ? `<div class="maint-ficha-actions"><a href="${esc(url)}">Abrir ficha canónica</a></div>` : ''}
      </div><div><span class="maint-meta">Estado técnico </span>${badge(item.status)}</div></div>
      <div class="maint-layer"><h4>Capa multimedia</h4>
      ${resourceGroup('Recursos propios', own, 'Sin recursos propios asociados.')}
      ${resourceGroup('Redes sociales', social, 'Sin publicaciones sociales vinculadas.')}
      ${other.length ? resourceGroup('Otros recursos externos', other, '') : ''}</div>
      ${issues.length ? `<div class="maint-checks"><div class="maint-layer-group-title">Comprobaciones de la ficha</div>${issues.map(c => `<div class="maint-check">${badge(c.status)} ${esc(c.label || c.kind || 'Comprobación')}: ${esc(c.detail || '')}</div>`).join('')}</div>` : ''}
      </article>`;
  }
  let categories=[];
  try{categories=JSON.parse(document.getElementById('maintenance-category-registry').textContent);}catch(_){root.textContent='No se pudo leer el registro de categorías.';return;}
  function pending() {
    const target=document.getElementById('marketing-unlinked'), state=C.inventoryState(report,failed?null:revision);
    if(!target)return;
    const list=state.pending.map(video=>{
      const url=C.safeURL(video.share_url,location.href);
      return el('article',{class:'maint-unlinked-card'},el('strong',{},video.title || 'Vídeo sin título registrado'),el('p',{class:'maint-meta'},'ID '+video.video_id),url?el('a',{href:url,target:'_blank',rel:'noopener noreferrer'},'Consultar publicación →'):null);
    });
    target.replaceChildren(el('section',{class:'maint-pending'},el('h3',{},'Pendientes de vinculación'),el('p',{class:'maint-meta'},'Inventario global de TikTok · No se limita por los filtros de fichas.'),el('span',{class:'workspace-tag','data-tone':state.known?'good':'neutral'},state.label),!state.known?el('p',{class:'maint-meta'},'No hay un inventario completo y vigente para afirmar cuántos recursos faltan por vincular. Las referencias anteriores, si existen, se conservan como históricas.'):null,...list));
  }
  function render() {
    pending();if(!report){return;}
    const wasOpen=root.querySelector('.maint-technical')?.open || false;
    const fresh=freshness(),rows=report.items.filter(i=>!selected||selected.has(i.code)), groups=groupItems(rows,categories,base);
    const tik=report.services?.tiktok || {}, checked=report.generated_at?new Date(report.generated_at).toLocaleString('es-ES'):'Sin fecha';
    lazy=new Map();
    const graph=groups.map(cat=>`<details class="catalog-category" data-technical-category="${esc(cat.id)}"><summary><strong>${esc(cat.name)}</strong></summary>${cat.roles.map(role=>`<details class="catalog-role" data-technical-role="${esc(role.id)}"><summary><strong>${esc(role.name)}</strong></summary>${role.sections.map(section=>{
      const key=cat.id+'|'+role.id+'|'+section.id;lazy.set(key,section.items);
      return `<details class="catalog-section" data-technical-section="${esc(section.id)}" data-lazy-key="${esc(key)}"><summary><strong>${esc(section.name)}</strong><span>${section.items.length} fichas</span></summary><div data-lazy-content></div></details>`;
    }).join('')}</details>`).join('')}</details>`).join('');
    const videoIds=new Set(rows.flatMap(i=>(i.media||[]).filter(a=>a.provider==='tiktok'&&a.video_id).map(a=>a.video_id)));
    const metrics=[[rows.length,'Fichas en este informe'],[videoIds.size,'Vídeos únicos registrados'],[fresh.current?rows.filter(i=>i.status==='ROTO').length:'—','Incidencias técnicas vigentes']];
    root.innerHTML=`<details class="maint-technical"${wasOpen?' open':''}><summary class="maint-technical-toggle"><strong>Informe técnico en detalle</strong><span>Diagnóstico por categoría, rol y sección</span></summary><div class="maint-technical-body">
      <div class="technical-freshness" data-current="${fresh.current}"><strong>${esc(fresh.label)}</strong><p class="maint-meta">Comprobación registrada: ${esc(checked)}. Vigencia: misma revisión del sitio y hasta 36 horas. El estado técnico no determina aprobación editorial.</p></div>
      <div class="maint-summary">${metrics.map(([value,label])=>`<div class="maint-card"><strong>${esc(value)}</strong><span>${esc(label)}</span></div>`).join('')}</div>
      <div class="maint-service"><div class="maint-service-head"><div><strong>TikTok · Servicio global</strong><p class="maint-meta">${esc(tik.detail || 'No se ha registrado una consulta al servicio.')}</p><p class="maint-meta">Vídeos detectados en la consulta registrada: ${esc(tik.recent_videos_checked ?? 'No determinado')}</p></div>${badge(tik.status)}</div></div>
      <h3>Diagnóstico de la selección</h3>${graph || '<p class="maint-empty">No hay fichas de estos filtros en el informe.</p>'}</div></details>`;
  }
  root.addEventListener('toggle',event=>{
    const details=event.target;
    if(!details.open||!details.dataset.lazyKey)return;
    const content=details.querySelector('[data-lazy-content]');
    if(content&&!content.children.length)content.innerHTML=(lazy.get(details.dataset.lazyKey)||[]).map(renderFicha).join('');
  },true);
  async function load(reload=false) {
    try {
      const result=await C.load(root.dataset.statusUrl,reload);
      if(!result||!Array.isArray(result.items))throw new Error('Formato de informe no válido');
      report=result;failed=false;window.__maintenanceData=result;window.__maintenanceReportError=false;
      render();window.dispatchEvent(new CustomEvent('maintenance:report',{detail:result}));
    }catch(error){
      failed=true;window.__maintenanceData=null;window.__maintenanceReportError=true;
      root.replaceChildren(el('h3',{},'Informe técnico no disponible'),el('p',{class:'maint-meta'},'No se pudo cargar el reporte: '+error.message+'. Puedes recargar los datos. La navegación, las fichas y los recursos publicados permanecen disponibles.'));
      pending();window.dispatchEvent(new Event('maintenance:report'));
    }
  }
  window.addEventListener('maintenance:scope',event=>{revision=event.detail.revision;selected=new Set(event.detail.codes);render();});
  window.addEventListener('maintenance:reload',()=>load(true));
  load();
})();
