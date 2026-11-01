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
.maint-summary { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:18px 0 28px; }
.maint-card { border:1px solid var(--line); background:var(--surface); border-radius:12px; padding:14px; }
.maint-card strong { display:block; font-size:1.45rem; }
.maint-card span { color:var(--muted); font-size:.82rem; }
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
.maint-meta { color:var(--muted); font-size:.84rem; margin-top:5px; }
.maint-resource { margin:10px 0 0; padding:10px 12px; background:var(--soft); border-radius:9px; font-size:.88rem; }
.maint-resource b { margin-right:6px; }
.maint-empty { color:var(--muted); }
@media(max-width:620px){ .maint-summary{grid-template-columns:1fr 1fr;} .maint-head{flex-direction:column;} }
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
    const rows = d.items.filter(i => state.filter === 'TODOS' || i.status === state.filter);
    root.innerHTML = `
      <p class="maint-meta">Última comprobación: ${esc(new Date(d.generated_at).toLocaleString('es-ES'))}</p>
      <div class="maint-summary">
        <div class="maint-card"><strong>${s.fichas}</strong><span>Fichas</span></div>
        <div class="maint-card"><strong>${s.recursos}</strong><span>Recursos</span></div>
        <div class="maint-card"><strong>${s.rotos}</strong><span>Con error</span></div>
        <div class="maint-card"><strong>${s.revisar}</strong><span>Por revisar</span></div>
      </div>
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
