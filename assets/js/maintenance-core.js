/* Shared, pure maintenance rules. Unknown evidence is never converted to success. */
((global) => {
  'use strict';
  const norm = value => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  function filterItems(items, f = {}) {
    const words = norm(f.query).split(/\s+/).filter(Boolean);
    return items.filter(i => (!f.category || i.category_id === f.category) &&
      (!f.role || i.role_id === f.role) && (!f.section || i.stage_url === f.section) &&
      words.every(w => norm([i.code, i.title, i.category, i.role, i.stage,
        i.source?.reference, ...(i.marketing_codes || [])].join(' ')).includes(w)));
  }
  function affectedBy(items, source, section = '') {
    return source ? items.filter(i => i.source?.label === source && (!section || (i.source.sections || []).includes(section))) : [];
  }
  function reviewMatches(i, kind) {
    if (kind === 'pending') return ['pending_review', 'changes_requested'].includes(i.editorial_status);
    if (kind === 'unspecified') return i.editorial_status === 'unspecified';
    if (kind === 'metadata') return Boolean(i.metadata_gaps?.length);
    if (kind.startsWith('gap:')) return (i.metadata_gaps || []).includes(kind.slice(4));
    if (kind === 'versions') return ['different_content', 'different_version'].includes(i.version_comparison);
    if (kind === 'media') return Boolean(i.stale_asset_ids?.length);
    if (kind === 'unverified') return Boolean(i.unverified_asset_ids?.length);
    if (kind === 'no-video') return !i.video_count;
    return false;
  }
  function reportState(report, revision, now = Date.now(), maxHours = 36) {
    if (!report) return {kind:'missing', label:'Sin informe disponible', current:false};
    const time = Date.parse(report.generated_at);
    if (!Number.isFinite(time) || time > now + 300000) return {kind:'unknown', label:'Fecha del informe no verificable', current:false};
    const source = report.revision || report.source_revision;
    if (!/^[0-9a-f]{40}$/i.test(source || '') || !/^[0-9a-f]{40}$/i.test(revision || '')) return {kind:'unknown', label:'Informe sin versión comprobable', current:false};
    if (source !== revision) return {kind:'mismatch', label:'Informe de otra versión', current:false};
    if (now - time > maxHours * 3600000) return {kind:'stale', label:'Comprobación anterior · actualizar', current:false};
    return {kind:'current', label:'Informe vigente · misma versión', current:true};
  }
  function technicalLabel(record) {
    return ({OK:'Correcto', REVISAR:'Requiere revisión técnica', ROTO:'Con incidencias', 'SIN COMPROBAR':'Sin comprobar'})[record?.status] || 'Sin comprobar';
  }
  function inventoryState(report, revision, now = Date.now()) {
    const fresh = reportState(report, revision, now);
    const inventory = report?.tiktok_inventory;
    const complete = inventory?.complete === true && report?.services?.tiktok?.status === 'OK';
    const videos = Array.isArray(inventory?.videos) ? inventory.videos : [];
    const pending = videos.filter(v => v.status === 'SIN VINCULAR');
    return {known:fresh.current && complete, pending, recorded:videos.length,
      label: fresh.current && complete ? (pending.length ? pending.length + ' pendientes de vincular' : 'Inventario comprobado · sin pendientes') : 'Pendientes sin comprobar'};
  }
  function summarize(items) {
    return {total:items.length, approved:items.filter(i => i.editorial_status === 'approved').length,
      pending:items.filter(i => ['pending_review','changes_requested'].includes(i.editorial_status)).length,
      unspecified:items.filter(i => i.editorial_status === 'unspecified').length,
      withVideo:items.filter(i => i.video_count > 0).length,
      noVideo:items.filter(i => !i.video_count).length,
      metadata:items.filter(i => i.metadata_gaps?.length).length,
      unverified:items.filter(i => i.unverified_asset_ids?.length).length};
  }
  function uniqueResources(items) {
    const map = new Map();
    items.forEach(item => {
      const assets = [...(item.media || []), ...(item.distribution || [])];
      assets.forEach(asset => {
        const key = asset.video_id ? (asset.provider || '') + ':' + asset.video_id : asset.id;
        if (!key) return;
        if (!map.has(key)) map.set(key, {...asset, title:(!asset.title || asset.title === asset.id) ? item.title : asset.title, key, placements:[], search_terms:[]});
        const linkedCodes=(item.marketing_pieces || []).filter(p=>(p.assets || []).some(a=>a.id===asset.id)).map(p=>p.code+' ('+(p.category_code || '')+')');
        map.get(key).search_terms.push(item.code,item.title,item.category,item.role,asset.id,...linkedCodes);
        const resource = map.get(key);
        if (!resource.placements.some(p => p.code === item.code)) resource.placements.push({
          code:item.code, title:item.title, canonical_url:item.canonical_url,
          media_url:asset.media_url, relation:asset.editorial_relation,
          content_version:item.content_version, derived_from_version:asset.derived_from_version,
        });
      });
    });
    return [...map.values()];
  }
  function safeURL(value, base) {
    if (!value) return '';
    try {
      const url = new URL(value, base || 'https://local.invalid');
      if (url.username || url.password || (url.protocol !== 'https:' && !(url.protocol === 'http:' && base && url.origin === new URL(base).origin))) return '';
      return url.href;
    } catch (_) { return ''; }
  }
  function csv(rows) {
    const cell = value => {
      let text = String(value ?? '');
      if (/^\s*[=+\-@]/.test(text) || /^[\t\r\n]/.test(text)) text = "'" + text;
      return '"' + text.replace(/"/g, '""') + '"';
    };
    return '\uFEFF' + rows.map(row => row.map(cell).join(';')).join('\r\n');
  }
  function download(rows, name) {
    const blob = new Blob([csv(rows)], {type:'text/csv;charset=utf-8;'});
    const url = URL.createObjectURL(blob), a = document.createElement('a');
    a.href = url; a.download = name; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  async function copy(value) {
    try { await navigator.clipboard.writeText(value); return true; } catch (_) {
      const previous=document.activeElement;
      const input = document.createElement('textarea');
      input.value = value; input.style.position = 'fixed'; input.style.opacity = '0';
      document.body.append(input); input.select();
      let ok = false; try { ok = document.execCommand('copy'); } catch (_) { /* report failure */ }
      input.remove(); if(previous?.isConnected)previous.focus({preventScroll:true}); return ok;
    }
  }
  const cache = new Map();
  function load(url, reload = false) {
    if (reload) cache.delete(url);
    if (!cache.has(url)) {
      const promise = fetch(url, {cache:'no-store'}).then(r => {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      }).catch(error => {cache.delete(url); throw error;});
      cache.set(url, promise);
    }
    return cache.get(url);
  }
  function node(tag, attrs = {}, ...children) {
    const el = document.createElement(tag);
    Object.entries(attrs).forEach(([key,value]) => el.setAttribute(key,String(value)));
    children.flat(Infinity).forEach(child => {if (child !== null && child !== undefined) el.append(child instanceof Node ? child : document.createTextNode(String(child)));});
    return el;
  }
  const api = {norm,filterItems,affectedBy,reviewMatches,reportState,technicalLabel,inventoryState,summarize,uniqueResources,safeURL,csv,download,copy,load,node};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else global.MaintenanceCore = api;
})(typeof window === 'undefined' ? globalThis : window);
