---
layout: default
title: "Centro de mantenimiento"
description: "Estado técnico y editorial de las fichas y recursos multimedia de Cómo funciona."
permalink: /mantenimiento/
eyebrow: "Mantenimiento · Cómo funciona"
---

# Centro de mantenimiento

Esta vista se genera automáticamente durante la publicación. Sirve para comprobar **vigencia de versiones, enlaces internos, archivos multimedia y videos externos**.

<div id="maintenance-dashboard" class="maintenance-dashboard" aria-live="polite">
  <p>Cargando estado del sistema…</p>
</div>

<style>
.maintenance-dashboard { margin-top: 24px; }
.maint-summary { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:10px; margin:18px 0 28px; }
.maint-card { border:1px solid var(--line); background:var(--surface); border-radius:12px; padding:14px; }
.maint-card strong { display:block; font-size:1.45rem; }
.maint-card span { color:var(--muted); font-size:.82rem; }
.maint-services { margin:0 0 28px; }
.maint-service { border:1px solid var(--line); background:var(--surface); border-radius:12px; padding:14px; }
.maint-service-head { display:flex; justify-content:space-between; gap:12px; align-items:center; }
.maint-filters { display:flex; flex-wrap:wrap; gap:8px; margin:0 0 18px; }
.maint-filters button { min-height:42px; border:1px solid var(--line); background:var(--surface); color:var(--text); border-radius:999px; padding:8px 13px; font:inherit; cursor:pointer; }
.maint-filters button[aria-pressed="true"] { border-color:var(--accent); }
.maint-item { border-top:1px solid var(--line); padding:18px 0; }
.maint-head { display:flex; justify-content:space-between; gap:12px; align-items:flex-start; }
.maint-head > div { min-width:0; }
.maint-code { color:var(--muted); font-size:.8rem; font-weight:700; }
.maint-status { white-space:nowrap; border:1px solid var(--line); border-radius:999px; padding:4px 9px; font-size:.78rem; font-weight:800; }
.maint-status[data-status="OK"] { border-color:#8DBA99; }
.maint-status[data-status="REVISAR"] { border-color:#D0A85B; }
.maint-status[data-status="ROTO"] { border-color:#D78787; }
.maint-status[data-status="SIN COMPROBAR"] { border-color:#AEB7B7; }
.maint-meta { color:var(--muted); font-size:.84rem; margin-top:5px; }
.maint-resource { margin:10px 0 0; padding:10px 12px; background:var(--soft); border-radius:9px; font-size:.88rem; }
.maint-resource b { margin-right:6px; }
.maint-empty { color:var(--muted); }
.maint-warning { margin-top:10px; padding:10px 12px; background:var(--soft); border-radius:9px; font-size:.88rem; }
.maint-inventory { margin: 30px 0 36px; }
.maint-inventory-head { display:flex; justify-content:space-between; gap:12px; align-items:flex-end; margin-bottom:12px; }
.maint-video { border-top:1px solid var(--line); padding:15px 0; }
.maint-video:first-of-type { border-top:0; }
.maint-video-title { font-weight:750; line-height:1.4; margin:4px 0; }
.maint-video-id { color:var(--muted); font-size:.78rem; word-break:break-all; }
.maint-video-links { margin-top:7px; font-size:.86rem; }
.maint-status[data-status="VINCULADO"] { border-color:#8DBA99; }
.maint-status[data-status="SIN VINCULAR"] { border-color:#D0A85B; }
@media(max-width:620px){ .maint-summary{grid-template-columns:1fr 1fr;} .maint-head,.maint-service-head,.maint-inventory-head{flex-direction:column;align-items:flex-start;} }
</style>

<script>
(() => {
  const root = document.getElementById('maintenance-dashboard');
  const statusUrl = "{{ '/mantenimiento/status.json' | relative_url }}";
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
  const state = { filter: 'TODOS', data: null };

  function render() {
    const d = state.data;
    if (!d) return;
    const s = d.summary;
    const tik = d.services?.tiktok || {status:'SIN COMPROBAR',detail:'Sin información'};
    const inv = d.tiktok_inventory || {total:0,linked:0,unlinked:0,videos:[]};
    const rows = d.items.filter(i => state.filter === 'TODOS' || i.status === state.filter);
    root.innerHTML = `
      <p class="maint-meta">Última comprobación: ${esc(new Date(d.generated_at).toLocaleString('es-ES'))}</p>
      <div class="maint-summary">
        <div class="maint-card"><strong>${s.fichas}</strong><span>Fichas</span></div>
        <div class="maint-card"><strong>${s.recursos}</strong><span>Recursos</span></div>
        <div class="maint-card"><strong>${s.videos_tiktok || 0}</strong><span>TikTok registrados</span></div>
        <div class="maint-card"><strong>${s.rotos}</strong><span>Con error</span></div>
        <div class="maint-card"><strong>${s.revisar}</strong><span>Por revisar</span></div>
      </div>
      <div class="maint-services">
        <div class="maint-service">
          <div class="maint-service-head">
            <div>
              <strong>TikTok API</strong>
              <div class="maint-meta">${esc(tik.detail || '')}</div>
              <div class="maint-meta">Videos recientes comprobados: ${esc(tik.recent_videos_checked ?? 0)}</div>
            </div>
            <span class="maint-status" data-status="${esc(tik.status)}">${esc(tik.status)}</span>
          </div>
          ${tik.rotation_required ? '<div class="maint-warning"><strong>Atención:</strong> TikTok devolvió un refresh token nuevo. Conviene habilitar la rotación automática del Secret de GitHub.</div>' : ''}
        </div>
      </div>
      <section class="maint-inventory">
        <div class="maint-inventory-head">
          <div>
            <h2>Inventario TikTok</h2>
            <div class="maint-meta">Detectados: ${esc(inv.total)} · Vinculados: ${esc(inv.linked)} · Sin vincular: ${esc(inv.unlinked)}</div>
          </div>
        </div>
        <div>
          ${inv.videos.length ? inv.videos.map(v => {
            const safeUrl = (v.share_url && String(v.share_url).startsWith('https://www.tiktok.com/'))
              ? v.share_url
              : ((v.embed_link && String(v.embed_link).startsWith('https://www.tiktok.com/')) ? v.embed_link : '');
            return `
              <article class="maint-video">
                <div class="maint-head">
                  <div>
                    <div class="maint-video-id">TikTok ID: ${esc(v.video_id)}</div>
                    <div class="maint-video-title">${esc(v.title || 'Sin título')}</div>
                    ${v.links?.length ? `<div class="maint-video-links">Ficha: ${v.links.map(l => `<a href="{{ site.baseurl }}${esc(l.canonical_url || '')}">${esc(l.code || l.title || 'Ficha')}</a>`).join(', ')}</div>` : '<div class="maint-video-links">Todavía no asociado a una ficha canónica.</div>'}
                    ${safeUrl ? `<div class="maint-video-links"><a href="${esc(safeUrl)}" target="_blank" rel="noopener noreferrer">Abrir video en TikTok</a></div>` : ''}
                  </div>
                  <span class="maint-status" data-status="${esc(v.status)}">${esc(v.status)}</span>
                </div>
              </article>`;
          }).join('') : '<p class="maint-empty">No se pudieron recuperar videos de TikTok.</p>'}
        </div>
      </section>
      <div class="maint-filters">
        ${['TODOS','OK','REVISAR','ROTO','SIN COMPROBAR'].map(x => `<button type="button" data-filter="${x}" aria-pressed="${state.filter===x}">${x}</button>`).join('')}
      </div>
      <div>
        ${rows.length ? rows.map(item => {
          const resources = [...(item.media || []), ...(item.checks || []).filter(c => c.status !== 'OK')];
          return `
            <section class="maint-item">
              <div class="maint-head">
                <div>
                  <div class="maint-code">${esc(item.code)}</div>
                  <strong>${esc(item.title)}</strong>
                  <div class="maint-meta">Versión canónica: ${esc(item.content_version ?? 'sin definir')} · Revisada: ${esc(item.reviewed || 'sin fecha')}</div>
                  ${item.canonical_url ? `<a href="{{ site.baseurl }}${esc(item.canonical_url)}">Abrir ficha</a>` : ''}
                </div>
                <span class="maint-status" data-status="${esc(item.status)}">${esc(item.status)}</span>
              </div>
              ${resources.length ? resources.map(r => `
                <div class="maint-resource">
                  <b>${esc(r.id || r.label || r.kind || 'Recurso')}</b>
                  <span class="maint-status" data-status="${esc(r.status)}">${esc(r.status)}</span><br>
                  ${esc(r.detail || '')}
                </div>`).join('') : '<p class="maint-empty">Sin incidencias registradas.</p>'}
            </section>`;
        }).join('') : '<p class="maint-empty">No hay elementos con este estado.</p>'}
      </div>`;

    root.querySelectorAll('[data-filter]').forEach(btn => {
      btn.addEventListener('click', () => {
        state.filter = btn.dataset.filter;
        render();
      });
    });
  }

  fetch(statusUrl, { cache: 'no-store' })
    .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(d => { state.data = d; render(); })
    .catch(err => { root.innerHTML = '<p>No se pudo cargar el reporte de mantenimiento: ' + esc(err.message) + '</p>'; });
})();
</script>
