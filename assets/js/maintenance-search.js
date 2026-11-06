/* Biblioteca pública de recursos, fichas y correspondencias editoriales.
 * Consume exclusivamente el catálogo generado por build_share_catalog.py.
 */
(() => {
  "use strict";
  const normalize = value => String(value == null ? "" : value)
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("es").trim();
  const publishedItems = values => Array.isArray(values)
    ? values.filter(item => item && item.public_searchable === true) : [];
  const productionCode = piece => (piece.code || "") +
    (piece.category_code ? " (" + piece.category_code + ")" : "");

  function matches(item, query, cat, selectedRole) {
    if (cat && item.category !== cat) return false;
    if (selectedRole && item.role !== selectedRole) return false;
    if (!query) return true;
    const pieces = [...(Array.isArray(item.media) ? item.media : []),
      ...(Array.isArray(item.distribution) ? item.distribution : [])];
    const marketing = Array.isArray(item.marketing_pieces) ? item.marketing_pieces : [];
    const editorial = Array.isArray(item.editorial_pieces) ? item.editorial_pieces : [];
    const haystack = normalize([
      item.code, item.title, item.category, item.role, item.stage,
      ...marketing.flatMap(piece => [productionCode(piece), piece.title, piece.category_code]),
      ...editorial.flatMap(piece => [productionCode(piece), piece.title, piece.relation]),
      ...pieces.flatMap(piece => [piece.title, piece.id, piece.provider, piece.type])
    ].filter(Boolean).join(" "));
    return normalize(query).split(/\s+/).every(token => haystack.includes(token));
  }

  if (typeof module !== "undefined" && module.exports) module.exports = { publishedItems, matches };
  if (typeof document === "undefined") return;
  const root = document.getElementById("maintenance-search");
  if (!root) return;

  const C=window.MaintenanceCore, el=C.node;
  const search=root.querySelector('#maint-search-text'), kind=root.querySelector('#media-kind'), provider=root.querySelector('#media-provider');
  const results=root.querySelector('#maint-search-results'), count=root.querySelector('#maint-search-count'), feedback=root.querySelector('#maint-search-feedback');
  const safeUrl=value=>C.safeURL(value,location.href);
  const node=(tag,className,text)=>el(tag,className?{class:className}:{},text);
  let items=[], scope=null, mode='resources', limit=12, exportRows=[];
  const selectedItems=()=>items.filter(i=>(!scope||scope.has(i.code))&&matches(i,search.value,'',''));
  const textMatches=values=>normalize(search.value).split(/\s+/).filter(Boolean).every(word=>normalize(values.flat(Infinity).join(' ')).includes(word));
  const providerMatches=asset=>!provider.value || (asset.provider || 'local')===provider.value;
  function copyButton(label, value, unavailable) {
    const button = node("button", "maint-search-copy", label);
    button.type = "button";
    const url = safeUrl(value);
    if (!url) {
      button.disabled = true;
      button.title = unavailable || "Enlace no disponible en los metadatos aprobados";
    } else {
      button.dataset.copyUrl = url;
      button.setAttribute("aria-label", label);
    }
    return button;
  }

  function linkActions(canonicalUrl, asset) {
    const actions = node("div", "maint-search-buttons");
    actions.appendChild(copyButton("Copiar ficha", canonicalUrl));
    actions.appendChild(copyButton("Copiar multimedia", asset && asset.media_url,
      "El recurso no está insertado en la ficha"));
    actions.appendChild(copyButton("Copiar original", asset && asset.original_url,
      "No consta una URL verificable de la publicación o archivo original"));
    return actions;
  }

  function assetRow(asset, canonicalUrl) {
    const row = node("div", "maint-search-piece maint-search-asset");
    const label = asset.provider || asset.type || "Recurso";
    row.appendChild(node("h5", "maint-search-piece-title", label + " · " + (asset.title || asset.id || "Sin título")));
    row.appendChild(node("p", "maint-search-meta", "ID técnico: " + (asset.id || "Sin ID") +
      (asset.media_url ? " · Multimedia dentro de la ficha" : " · Publicación distribuida")));
    row.appendChild(linkActions(canonicalUrl, asset));
    return row;
  }

  function resultCard(item) {
    const card = node("article", "maint-search-result");
    card.appendChild(node("p", "maint-search-ficha-code", "Ficha canónica · " + (item.code || "Sin código")));
    card.appendChild(node("h3", "maint-search-heading", item.title || "Sin título"));
    card.appendChild(node("p", "maint-search-meta", [item.category, item.role, item.stage].filter(Boolean).join(" · ")));

    // Las correspondencias aprobadas no afirman que exista una publicación.
    // Los recursos se vinculan por separado mediante asset_ids verificados.
    const editorial = Array.isArray(item.editorial_pieces) ? item.editorial_pieces : [];
    const verified = Array.isArray(item.marketing_pieces) ? item.marketing_pieces : [];
    const byCode = new Map();
    editorial.forEach(piece => byCode.set(piece.code, { ...piece, assets: [] }));
    verified.forEach(piece => {
      const prior = byCode.get(piece.code);
      byCode.set(piece.code, prior
        ? { ...prior, ...piece, relation: prior.relation, assets: piece.assets || [] }
        : piece);
    });
    const linkedPieces = [...byCode.values()];
    const fallbackAssets = [...(Array.isArray(item.media) ? item.media : []),
      ...(Array.isArray(item.distribution) ? item.distribution : [])];
    const unassigned = Array.isArray(item.unassigned_assets) ? item.unassigned_assets : fallbackAssets;

    card.appendChild(node("p", "maint-search-meta", linkedPieces.length
      ? linkedPieces.length + (linkedPieces.length === 1 ? " pieza publicitaria relacionada" : " piezas publicitarias relacionadas")
      : "Sin correspondencia editorial de pieza publicitaria"));

    linkedPieces.forEach(piece => {
      const group = node("section", "maint-search-piece maint-search-production");
      const officialCode = (piece.code || "Sin código") +
        (piece.category_code ? " (" + piece.category_code + ")" : "");
      group.appendChild(node("h4", "maint-search-piece-title", "Pieza publicitaria · " + officialCode));
      group.appendChild(node("p", "maint-search-meta", piece.title || "Título no registrado"));
      group.appendChild(node("p", "maint-search-meta", piece.relation
        ? "Correspondencia " + piece.relation.toLowerCase() + " · Ensamblaje editorial aprobado"
        : "Publicación asociada mediante metadatos verificados"));
      const assets = Array.isArray(piece.assets) ? piece.assets : [];
      if (!assets.length) {
        group.appendChild(node("p", "maint-search-empty",
          "Relación editorial aprobada; todavía no consta multimedia o publicación verificada para esta pieza."));
        group.appendChild(linkActions(item.canonical_url, null));
      } else {
        assets.forEach(asset => group.appendChild(assetRow(asset, item.canonical_url)));
      }
      card.appendChild(group);
    });

    if (unassigned.length) {
      const group = node("section", "maint-search-piece maint-search-unassigned");
      group.appendChild(node("h4", "maint-search-piece-title", "Recursos y publicaciones sin pieza publicitaria identificada"));
      group.appendChild(node("p", "maint-search-meta", "Se conserva su vínculo con la ficha, pero no se presupone un código de producción."));
      unassigned.forEach(asset => group.appendChild(assetRow(asset, item.canonical_url)));
      card.appendChild(group);
    } else if (!linkedPieces.length) {
      card.appendChild(node("p", "maint-search-empty", "Esta ficha no tiene publicaciones aprobadas asociadas."));
      card.appendChild(linkActions(item.canonical_url, null));
    }
    return card;
  }

  function isUnknown(resource) {return resource.placements.some(p=>p.content_version==null||p.derived_from_version==null);}
  function resourceMatches(resource) {
    if(!providerMatches(resource) || !textMatches([resource.title,resource.type,resource.provider,resource.id,resource.search_terms]))return false;
    if(!kind.value)return true;
    if(kind.value==='unverified')return isUnknown(resource);
    if(kind.value==='missing-origin')return !resource.original_url;
    return resource.type===kind.value;
  }
  function action(label,url) {const target=safeUrl(url);return target?el('a',{href:target,target:'_blank',rel:'noopener noreferrer'},label):null;}
  function resourceCard(resource) {
    let previews={};try{previews=JSON.parse(document.getElementById('maintenance-visual-previews').textContent)||{};}catch(_){/* no decorative preview */}
    const base=document.getElementById('maintenance-dashboard').dataset.baseurl || '';
    const preview=previews[resource.id];
    const visual=el('div',{class:'media-resource-preview'},preview?el('img',{src:base+preview,alt:'',loading:'lazy',width:'720',height:'480'}):[el('span',{'aria-hidden':'true'},resource.type==='video'?'▷':'◇'),el('strong',{},String(resource.provider||resource.type||'recurso').toUpperCase())]);
    const first=resource.placements[0];
    const title=resource.title===resource.id?first.title:resource.title || first.title;
    const places=el('details',{class:'media-placements'},el('summary',{},resource.placements.length+' fichas vinculadas'),resource.placements.map(p=>el('a',{href:safeUrl(p.media_url || p.canonical_url)},p.code+' · '+p.title)));
    const controls=el('div',{class:'media-resource-actions'},action('Ver en la ficha →',first.media_url || first.canonical_url),action('Origen →',resource.original_url),copyButton('Copiar recurso',first.media_url,'No hay ancla registrada'));
    return el('article',{class:'media-resource-card','data-resource-key':resource.key},visual,el('div',{class:'media-resource-body'},el('span',{class:'workspace-tag'},({video:'Vídeo',diagram:'Diagrama',animation:'Animación',image:'Imagen'})[resource.type] || 'Recurso'),el('h4',{},title),el('p',{class:'maint-meta'},resource.placements.length+' ubicaciones en fichas · '+(isUnknown(resource)?'Versión de origen por contrastar':'Versión de origen registrada')),controls,places));
  }
  function compactFicha(item) {
    const card=resultCard(item), groups=[...card.querySelectorAll('.maint-search-piece,.maint-search-unassigned')];
    if(groups.length){const details=el('details',{class:'media-placements'},el('summary',{},'Ver relaciones y enlaces ('+groups.length+')'));groups.forEach(group=>details.append(group));card.append(details);}
    card.append(el('button',{type:'button',class:'workspace-button','data-open-control':item.code},'Ver control de ficha →'));
    return card;
  }
  function piecesFor(rows) {
    const map=new Map();
    rows.forEach(item=>{
      const verified=new Map((item.marketing_pieces||[]).map(p=>[p.code,p]));
      const associations=[...(item.editorial_pieces||[])];
      verified.forEach(piece=>{if(!associations.some(p=>p.code===piece.code))associations.push(piece);});
      associations.forEach(piece=>{
        const key=(piece.category_code||item.category)+'|'+piece.code;
        if(!map.has(key))map.set(key,{...piece,key,placements:[],assets:new Map(),unverified:false});
        const target=map.get(key);target.placements.push({code:item.code,title:item.title,url:item.canonical_url,relation:piece.relation});
        (verified.get(piece.code)?.assets||[]).forEach(a=>{target.assets.set(a.provider+':'+(a.video_id||a.id),a);if(a.derived_from_version==null||item.content_version==null)target.unverified=true;});
      });
    });
    return [...map.values()].map(p=>({...p,assets:[...p.assets.values()]}));
  }
  function pieceCard(piece) {
    return el('article',{class:'piece-card'},el('span',{class:'piece-code'},piece.code+' · '+(piece.category_code||'Categoría registrada')),el('h4',{},piece.title),el('span',{class:'workspace-tag','data-tone':piece.assets.length?'good':'neutral'},piece.assets.length?'Con publicación vinculada':'Relación editorial · Sin publicación registrada'),el('p',{class:'maint-meta'},piece.placements.length+' fichas relacionadas'),el('details',{class:'media-placements'},el('summary',{},'Consultar correspondencias'),piece.placements.map(p=>el('a',{href:safeUrl(p.url)},p.code+' · '+(p.relation||'Relación registrada')))));
  }
  function pieceMatches(piece) {
    if(!textMatches([piece.code,piece.title,piece.category_code,piece.placements.flatMap(p=>[p.code,p.title])]))return false;
    if(provider.value&&!piece.assets.some(providerMatches))return false;
    if(!kind.value)return true;
    if(kind.value==='unverified')return piece.unverified;
    if(kind.value==='missing-origin')return piece.assets.some(a=>!a.original_url);
    return piece.assets.some(a=>a.type===kind.value);
  }
  function syncURL() {
    const url=new URL(location.href);
    [['media',mode==='resources'?'':mode],['refine',search.value],['kind',kind.value],['provider',provider.value]].forEach(([key,value])=>value?url.searchParams.set(key,value):url.searchParams.delete(key));
    history.replaceState(null,'',url);
  }
  function render() {
    if(!items.length){exportRows=[];count.textContent='Catálogo sin fichas publicables';document.getElementById('media-coverage').replaceChildren();results.replaceChildren(node('p','maint-search-empty','No hay fichas publicables disponibles en el catálogo.'));document.getElementById('maint-search-more').hidden=true;return;}
    if(kind.value==='no-video')mode='fichas';
    let rows=selectedItems();
    const scoped=items.filter(i=>!scope||scope.has(i.code)), resources=C.uniqueResources(scoped), videoResources=resources.filter(r=>r.type==='video');
    const withVideo=scoped.filter(i=>(i.media||[]).some(a=>a.type==='video')).length;
    document.getElementById('media-coverage').replaceChildren(...[[resources.length,'recursos únicos'],[videoResources.length,'vídeos únicos'],[resources.reduce((n,r)=>n+r.placements.length,0),'ubicaciones'],[withVideo,'fichas con vídeo'],[scoped.length-withVideo,'sin vídeo publicado']].map(([value,label])=>el('div',{},el('strong',{},value),label)));
    let renderRow, unit;
    if(mode==='resources'){
      rows=resources.filter(resourceMatches);renderRow=resourceCard;unit='recursos únicos';
      exportRows=[['Tipo','Título','Proveedor','Ubicaciones','Fichas','Publicación original'],...rows.map(r=>[r.type,r.title,r.provider,r.placements.length,r.placements.map(p=>p.code).join(' | '),r.original_url])];
    } else if(mode==='pieces') {
      rows=piecesFor(scoped).filter(pieceMatches);renderRow=pieceCard;unit='piezas editoriales';
      exportRows=[['Código de pieza','Título','Categoría','Publicaciones vinculadas','Fichas'],...rows.map(p=>[p.code,p.title,p.category_code,p.assets.length,p.placements.map(x=>x.code).join(' | ')])];
    } else {
      rows=rows.filter(i=>kind.value==='no-video'?!(i.media||[]).some(a=>a.type==='video'):!kind.value?true:kind.value==='unverified'?(i.media||[]).some(a=>a.derived_from_version==null||i.content_version==null):kind.value==='missing-origin'?(i.media||[]).some(a=>!a.original_url):(i.media||[]).some(a=>a.type===kind.value));
      if(provider.value)rows=rows.filter(i=>[...(i.media||[]),...(i.distribution||[])].some(providerMatches));
      renderRow=compactFicha;unit='fichas';
      exportRows=[['Código','Título','Categoría','Rol','URL'],...rows.map(i=>[i.code,i.title,i.category,i.role,i.canonical_url])];
    }
    count.textContent='Mostrando '+Math.min(limit,rows.length)+' de '+rows.length+' '+unit+' · Filtros actuales';
    results.replaceChildren(...(rows.length?rows.slice(0,limit).map(renderRow):[el('div',{class:'workspace-empty'},el('strong',{},'No hay coincidencias'),node('p','maint-meta','Prueba otro refinamiento o cambia los filtros del espacio de trabajo.'))]));
    document.getElementById('maint-search-more').hidden=rows.length<=limit;
    root.querySelectorAll('[data-media-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mediaMode===mode)));
    syncURL();
  }
  async function load(reload=false) {
    try {
      const data=await C.load(root.dataset.catalogUrl,reload);
      if(!Array.isArray(data.items))throw new Error('Catálogo no válido');
      items=publishedItems(data.items);
      const previous=provider.value || new URL(location.href).searchParams.get('provider');
      provider.replaceChildren(new Option('Todos los proveedores',''));
      [...new Set(C.uniqueResources(items).map(r=>r.provider||'local'))].sort().forEach(value=>provider.add(new Option(value==='local'?'Archivo local':value,value)));
      if([...provider.options].some(o=>o.value===previous))provider.value=previous;
      const a=data.editorial_assembly;
      const label=root.querySelector('#maint-assembly-summary');
      label.textContent=a?'Registro editorial completo de FR: '+a.pieces+' piezas y '+a.relations+' relaciones aprobadas. Las cifras de resultados corresponden a los filtros actuales.':'';
      window.dispatchEvent(new CustomEvent('maintenance:shared',{detail:{items}}));
      render();
    }catch(error){exportRows=[];count.textContent='Catálogo no disponible';document.getElementById('media-coverage').replaceChildren();results.replaceChildren(node('p','maint-search-empty','No se pudo cargar el catálogo de enlaces: '+error.message+'. Puedes recargar los datos sin perder los filtros.'));document.getElementById('maint-search-more').hidden=true;}
  }
  function restore(){
    const saved=new URL(location.href).searchParams;
    mode=['resources','fichas','pieces'].includes(saved.get('media'))?saved.get('media'):'resources';
    search.value=(saved.get('refine')||'').slice(0,160);
    kind.value=[...kind.options].some(o=>o.value===saved.get('kind'))?saved.get('kind'):'';
    provider.value=[...provider.options].some(o=>o.value===saved.get('provider'))?saved.get('provider'):'';
    limit=12;
  }
  restore();
  search.addEventListener('input',()=>{limit=12;render();});
  kind.addEventListener('change',()=>{limit=12;render();});
  provider.addEventListener('change',()=>{limit=12;render();});
  root.querySelectorAll('[data-media-mode]').forEach(b=>b.addEventListener('click',()=>{mode=b.dataset.mediaMode;if(kind.value==='no-video')kind.value='';limit=12;render();}));
  root.querySelector('#maint-search-clear').addEventListener('click',()=>{search.value='';kind.value='';provider.value='';limit=12;feedback.textContent='';render();search.focus();});
  root.querySelector('#maint-search-more').addEventListener('click',()=>{limit+=12;render();});
  results.addEventListener('click',async event=>{const b=event.target.closest('button[data-copy-url]');if(b)feedback.textContent=await C.copy(b.dataset.copyUrl)?'Enlace copiado: '+b.dataset.copyUrl:'No se pudo copiar. Puedes abrir el destino para copiar su dirección.';});
  window.addEventListener('maintenance:scope',event=>{scope=new Set(event.detail.codes);limit=12;render();});
  window.addEventListener('maintenance:topic',event=>{mode='fichas';kind.value='';search.value=event.detail.code;limit=12;render();search.focus();});
  window.addEventListener('maintenance:restore',restore);
  window.addEventListener('maintenance:reload',()=>load(true));
  window.addEventListener('maintenance:export',()=>{if(exportRows.length)C.download(exportRows,'mantenimiento-multimedia.csv');});
  load();
})();
