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
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  const base = root.dataset.baseurl || '';
  const socialProviders = new Set(['youtube','facebook','instagram','tiktok','x','linkedin']);
  const names = {youtube:'YouTube',facebook:'Facebook',instagram:'Instagram',tiktok:'TikTok',x:'X',linkedin:'LinkedIn'};
  function safeUrl(value) {
    const s = String(value || '');
    if (/^https?:\/\//i.test(s)) return s;
    if (/^\/(?!\/)/.test(s)) return base && !s.startsWith(base + '/') ? base + s : s;
    return '';
  }
  function badge(status) { return `<span class="maint-status" data-status="${esc(status || 'SIN COMPROBAR')}">${esc(status || 'SIN COMPROBAR')}</span>`; }
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
  function render(data, categories) {
    const summary = data.summary || {};
    const tik = data.services?.tiktok || {status:'SIN COMPROBAR', detail:'Sin información'};
    const inventory = data.tiktok_inventory || {videos:[]};
    const groups = groupItems(data.items || [], categories, base);
    const pending = (inventory.videos || []).filter(v => v.status === 'SIN VINCULAR');
    const checked = data.generated_at ? new Date(data.generated_at).toLocaleString('es-ES') : 'Sin fecha';
    root.innerHTML = `<details class="maint-technical"><summary class="maint-technical-toggle"><strong>Ver mantenimiento técnico</strong><span>Estado de fichas, recursos, servicios y pendientes</span></summary><div class="maint-technical-body">
      <p class="maint-meta">Última comprobación: ${esc(checked)}. El estado técnico no determina la aprobación editorial.</p>
      <div class="maint-summary">${[['fichas','Fichas'],['recursos','Recursos propios'],['videos_tiktok','TikTok vinculados'],['rotos','Con error'],['revisar','Por revisar técnicamente']].map(([key,label]) => `<div class="maint-card"><strong>${esc(summary[key] || 0)}</strong><span>${label}</span></div>`).join('')}</div>
      <div class="maint-service"><div class="maint-service-head"><div><strong>TikTok API</strong><div class="maint-meta">${esc(tik.detail || '')}</div><div class="maint-meta">Videos públicos detectados: ${esc(tik.recent_videos_checked ?? 0)}</div></div>${badge(tik.status)}</div></div>
      <h2>Diagnóstico por categoría, rol y sección</h2>
      ${groups.map(cat => `<details class="catalog-category" data-technical-category="${esc(cat.id)}"><summary><strong>${esc(cat.name)}</strong></summary>${cat.roles.map(role => `<details class="catalog-role" data-technical-role="${esc(role.id)}"><summary><strong>${esc(role.name)}</strong></summary>${role.sections.map(section => `<details class="catalog-section" data-technical-section="${esc(section.id)}"><summary><strong>${esc(section.name)}</strong><span>${section.items.length} fichas</span></summary>${section.items.map(renderFicha).join('')}</details>`).join('')}</details>`).join('')}</details>`).join('') || '<p class="maint-empty">No hay fichas en este reporte técnico.</p>'}
      <section class="maint-pending"><h2>Pendientes de vinculación</h2><p class="maint-meta">Recursos detectados en redes sociales que todavía no tienen una ficha canónica asignada.</p><h3>TikTok</h3>
      ${pending.length ? pending.map(video => {
        const candidate = [video.share_url, video.embed_link].find(url => String(url || '').startsWith('https://www.tiktok.com/'));
        return `<div class="maint-unlinked-card"><div class="maint-unlinked-title">${esc(video.title || 'Sin título')}</div><div class="maint-unlinked-id">Video ID: ${esc(video.video_id)}</div>${candidate ? `<div class="maint-resource-actions"><a href="${esc(candidate)}" target="_blank" rel="noopener noreferrer">Abrir en TikTok</a></div>` : ''}</div>`;
      }).join('') : '<div class="maint-empty">No hay videos TikTok pendientes de vinculación.</div>'}</section></div></details>`;
  }
  let categories;
  try { categories = JSON.parse(document.getElementById('maintenance-category-registry').textContent); }
  catch (_) { root.textContent = 'No se pudo leer la configuración de categorías. La estructura de contenido permanece disponible.'; return; }
  fetch(root.dataset.statusUrl, {cache:'no-store'})
    .then(response => { if (!response.ok) throw new Error('HTTP ' + response.status); return response.json(); })
    .then(data => { window.__maintenanceData = data; render(data, categories); })
    .catch(error => { root.textContent = 'No se pudo cargar el reporte de mantenimiento: ' + error.message + '. La estructura y el buscador de fichas permanecen disponibles.'; });
})();
