---
layout: default
title: "Centro de mantenimiento"
description: "Estado técnico y editorial de las fichas y recursos multimedia de Cómo funciona."
permalink: /mantenimiento/
eyebrow: "Mantenimiento · Cómo funciona"
---

# Centro de mantenimiento

La vista sigue la misma estructura de **Cómo funciona**: **Etapa → Ficha → Capa multimedia**. Los recursos todavía sin ficha se mantienen aparte como pendientes de vinculación.

<div id="maintenance-dashboard" class="maintenance-dashboard" aria-live="polite">
  <p>Cargando estado del sistema…</p>
</div>

<style>
.maintenance-dashboard { margin-top:24px; }
.maint-summary { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:10px; margin:18px 0 28px; }
.maint-card,.maint-service,.maint-ficha,.maint-unlinked-card { border:1px solid var(--line); background:var(--surface); border-radius:12px; }
.maint-card { padding:14px; }
.maint-card strong { display:block; font-size:1.45rem; }
.maint-card span,.maint-meta { color:var(--muted); font-size:.82rem; }
.maint-service { padding:14px; margin-bottom:28px; }
.maint-service-head,.maint-ficha-head,.maint-layer-head { display:flex; justify-content:space-between; gap:14px; align-items:flex-start; }
.maint-status { white-space:nowrap; border:1px solid var(--line); border-radius:999px; padding:4px 9px; font-size:.76rem; font-weight:800; }
.maint-status[data-status="OK"],.maint-status[data-status="VINCULADO"] { border-color:#8DBA99; }
.maint-status[data-status="REVISAR"],.maint-status[data-status="SIN VINCULAR"] { border-color:#D0A85B; }
.maint-status[data-status="ROTO"] { border-color:#D78787; }
.maint-status[data-status="SIN COMPROBAR"] { border-color:#AEB7B7; }

.maint-stage { margin:28px 0 34px; }
.maint-stage > summary { list-style:none; cursor:pointer; padding:14px 0; border-bottom:1px solid var(--line); }
.maint-stage > summary::-webkit-details-marker { display:none; }
.maint-stage-title { font-size:1.28rem; font-weight:800; }
.maint-stage-meta { color:var(--muted); font-size:.82rem; margin-top:3px; }

.maint-ficha { padding:16px; margin:14px 0; }
.maint-code { color:var(--muted); font-size:.78rem; font-weight:800; }
.maint-ficha-title { font-weight:800; margin-top:3px; line-height:1.35; }
.maint-ficha-actions { margin-top:7px; font-size:.86rem; }

.maint-layer { margin-top:16px; padding-top:14px; border-top:1px solid var(--line); }
.maint-layer h4 { margin:0; font-size:.96rem; }
.maint-layer-group { margin-top:12px; }
.maint-layer-group-title { color:var(--muted); font-size:.78rem; text-transform:uppercase; letter-spacing:.05em; font-weight:800; margin-bottom:6px; }
.maint-resource { background:var(--soft); border-radius:9px; padding:11px 12px; margin:7px 0; font-size:.86rem; }
.maint-resource-head { display:flex; justify-content:space-between; gap:10px; align-items:flex-start; }
.maint-resource-name { font-weight:750; }
.maint-resource-meta { color:var(--muted); font-size:.8rem; margin-top:4px; overflow-wrap:anywhere; }
.maint-resource-actions { display:flex; gap:12px; flex-wrap:wrap; margin-top:7px; }

.maint-checks { margin-top:12px; }
.maint-check { font-size:.82rem; color:var(--muted); margin:4px 0; }
.maint-empty { color:var(--muted); font-size:.85rem; }

.maint-pending { margin-top:38px; padding-top:22px; border-top:2px solid var(--line); }
.maint-pending h2 { margin-bottom:5px; }
.maint-unlinked-card { padding:13px; margin:9px 0; }
.maint-unlinked-title { font-weight:750; line-height:1.4; }
.maint-unlinked-id { color:var(--muted); font-size:.78rem; margin-top:5px; overflow-wrap:anywhere; }

@media(max-width:620px){
  .maint-summary{grid-template-columns:1fr 1fr;}
  .maint-service-head,.maint-ficha-head,.maint-resource-head{flex-direction:column;}
}
</style>

<script>
(() => {
  const root = document.getElementById('maintenance-dashboard');
  const statusUrl = "{{ '/mantenimiento/status.json' | relative_url }}";
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));

  const socialProviders = new Set(['youtube','facebook','instagram','tiktok','x','linkedin']);

  function resourceUrl(r) {
    if (r?.url && /^https?:\/\//.test(String(r.url))) return r.url;
    if (r?.src && /^https?:\/\//.test(String(r.src))) return r.src;
    return '';
  }

  function providerLabel(r) {
    if (r.storage === 'internal') return r.type || 'Recurso propio';
    const p = String(r.provider || '').toLowerCase();
    const names = {youtube:'YouTube',facebook:'Facebook',instagram:'Instagram',tiktok:'TikTok',x:'X',linkedin:'LinkedIn'};
    return names[p] || r.provider || r.type || 'Recurso externo';
  }

  function renderResource(r) {
    const url = resourceUrl(r);
    const version = [r.version ?? '—', r.derived_from_version ?? '—'].join(' / ');
    return `
      <div class="maint-resource">
        <div class="maint-resource-head">
          <div>
            <div class="maint-resource-name">${esc(providerLabel(r))} · ${esc(r.id || 'Sin ID')}</div>
            ${r.title ? `<div class="maint-resource-meta">${esc(r.title)}</div>` : ''}
            ${r.video_id ? `<div class="maint-resource-meta">Video ID: ${esc(r.video_id)}</div>` : ''}
            <div class="maint-resource-meta">Versión recurso / derivada: ${esc(version)}</div>
            ${r.detail ? `<div class="maint-resource-meta">${esc(r.detail)}</div>` : ''}
          </div>
          <span class="maint-status" data-status="${esc(r.status)}">${esc(r.status)}</span>
        </div>
        ${url ? `<div class="maint-resource-actions"><a href="${esc(url)}" target="_blank" rel="noopener noreferrer">Abrir recurso</a></div>` : ''}
      </div>`;
  }

  function renderFicha(item) {
    const media = item.media || [];
    const own = media.filter(r => r.storage === 'internal');
    const social = media.filter(r => socialProviders.has(String(r.provider || '').toLowerCase()));
    const other = media.filter(r => r.storage !== 'internal' && !socialProviders.has(String(r.provider || '').toLowerCase()));
    const issues = (item.checks || []).filter(c => c.status !== 'OK');

    return `
      <article class="maint-ficha">
        <div class="maint-ficha-head">
          <div>
            <div class="maint-code">${esc(item.code)}</div>
            <div class="maint-ficha-title">${esc(item.title)}</div>
            <div class="maint-meta">Versión canónica: ${esc(item.content_version ?? 'sin definir')} · Revisada: ${esc(item.reviewed || 'sin fecha')}</div>
            ${item.canonical_url ? `<div class="maint-ficha-actions"><a href="{{ site.baseurl }}${esc(item.canonical_url)}">Abrir ficha canónica</a></div>` : ''}
          </div>
          <span class="maint-status" data-status="${esc(item.status)}">${esc(item.status)}</span>
        </div>

        <div class="maint-layer">
          <div class="maint-layer-head"><h4>Capa multimedia</h4></div>

          <div class="maint-layer-group">
            <div class="maint-layer-group-title">Recursos propios</div>
            ${own.length ? own.map(renderResource).join('') : '<div class="maint-empty">Sin recursos propios asociados.</div>'}
          </div>

          <div class="maint-layer-group">
            <div class="maint-layer-group-title">Redes sociales</div>
            ${social.length ? social.map(renderResource).join('') : '<div class="maint-empty">Sin publicaciones sociales vinculadas.</div>'}
          </div>

          ${other.length ? `
          <div class="maint-layer-group">
            <div class="maint-layer-group-title">Otros recursos externos</div>
            ${other.map(renderResource).join('')}
          </div>` : ''}
        </div>

        ${issues.length ? `
        <div class="maint-checks">
          <div class="maint-layer-group-title">Comprobaciones de la ficha</div>
          ${issues.map(c => `<div class="maint-check"><span class="maint-status" data-status="${esc(c.status)}">${esc(c.status)}</span> ${esc(c.label || c.kind || 'Comprobación')}: ${esc(c.detail || '')}</div>`).join('')}
        </div>` : ''}
      </article>`;
  }

  function render() {
    const d = window.__maintenanceData;
    if (!d) return;
    const s = d.summary || {};
    const tik = d.services?.tiktok || {status:'SIN COMPROBAR',detail:'Sin información'};
    const inv = d.tiktok_inventory || {total:0,linked:0,unlinked:0,videos:[]};

    const stageMap = new Map();
    (d.items || []).forEach(item => {
      const key = String(item.stage_order ?? 999).padStart(3,'0') + '|' + (item.stage || 'Sin etapa');
      if (!stageMap.has(key)) stageMap.set(key, {order:item.stage_order ?? 999, name:item.stage || 'Sin etapa', items:[]});
      stageMap.get(key).items.push(item);
    });
    const stages = [...stageMap.values()].sort((a,b) => a.order - b.order);

    const unlinked = (inv.videos || []).filter(v => v.status === 'SIN VINCULAR');

    root.innerHTML = `
      <p class="maint-meta">Última comprobación: ${esc(new Date(d.generated_at).toLocaleString('es-ES'))}</p>

      <div class="maint-summary">
        <div class="maint-card"><strong>${s.fichas || 0}</strong><span>Fichas</span></div>
        <div class="maint-card"><strong>${s.recursos || 0}</strong><span>Recursos propios</span></div>
        <div class="maint-card"><strong>${s.videos_tiktok || 0}</strong><span>TikTok vinculados</span></div>
        <div class="maint-card"><strong>${s.rotos || 0}</strong><span>Con error</span></div>
        <div class="maint-card"><strong>${s.revisar || 0}</strong><span>Por revisar</span></div>
      </div>

      <div class="maint-service">
        <div class="maint-service-head">
          <div>
            <strong>TikTok API</strong>
            <div class="maint-meta">${esc(tik.detail || '')}</div>
            <div class="maint-meta">Videos públicos detectados: ${esc(tik.recent_videos_checked ?? 0)}</div>
          </div>
          <span class="maint-status" data-status="${esc(tik.status)}">${esc(tik.status)}</span>
        </div>
      </div>

      <h2>Mantenimiento por recorrido</h2>
      ${stages.map((stage, idx) => `
        <details class="maint-stage" ${idx === 0 ? 'open' : ''}>
          <summary>
            <div class="maint-stage-title">${String(stage.order).padStart(2,'0')} · ${esc(stage.name)}</div>
            <div class="maint-stage-meta">${stage.items.length} fichas</div>
          </summary>
          ${stage.items.map(renderFicha).join('')}
        </details>
      `).join('')}

      <section class="maint-pending">
        <h2>Pendientes de vinculación</h2>
        <p class="maint-meta">Recursos detectados en redes sociales que todavía no tienen una ficha canónica asignada.</p>
        <h3>TikTok</h3>
        ${unlinked.length ? unlinked.map(v => {
          const safeUrl = (v.share_url && String(v.share_url).startsWith('https://www.tiktok.com/'))
            ? v.share_url
            : ((v.embed_link && String(v.embed_link).startsWith('https://www.tiktok.com/')) ? v.embed_link : '');
          return `
            <div class="maint-unlinked-card">
              <div class="maint-unlinked-title">${esc(v.title || 'Sin título')}</div>
              <div class="maint-unlinked-id">Video ID: ${esc(v.video_id)}</div>
              ${safeUrl ? `<div class="maint-resource-actions"><a href="${esc(safeUrl)}" target="_blank" rel="noopener noreferrer">Abrir en TikTok</a></div>` : ''}
            </div>`;
        }).join('') : '<div class="maint-empty">No hay videos TikTok pendientes de vinculación.</div>'}
      </section>
    `;
  }

  fetch(statusUrl, {cache:'no-store'})
    .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(d => { window.__maintenanceData = d; render(); })
    .catch(err => { root.innerHTML = '<p>No se pudo cargar el reporte de mantenimiento: ' + esc(err.message) + '</p>'; });
})();
</script>
