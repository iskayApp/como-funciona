const test=require('node:test');
const assert=require('node:assert/strict');
const {norm,filterItems,affectedBy,reviewMatches,technicalLabel}=require('../assets/js/maintenance-workspace.js');
const items=[
 {code:'CF-001',title:'Garantía y documentación',category_id:'a',role_id:'p',stage_url:'/a/p/s/',editorial_status:'pending_review',source:{label:'Guía A',sections:['Sección 1'],reference:'Guía A — Sección 1'},metadata_gaps:['guide_version'],stale_asset_ids:[],version_comparison:'no_reference'},
 {code:'CF-002',title:'Garantía hipotecaria',category_id:'b',role_id:'p',stage_url:'/b/p/s/',editorial_status:'unspecified',source:{label:'Guía B',sections:['Sección 1'],reference:'Guía B — Sección 1'},metadata_gaps:['editorial_state'],stale_asset_ids:[],version_comparison:'same_version_unverified'}
];
test('filters are accent insensitive and category scoped',()=>{assert.equal(norm('GARANTÍA'),'garantia'); assert.equal(filterItems(items,{query:'garantia',category:'a'}).length,1); assert.equal(filterItems(items,{section:'/b/p/s/'})[0].code,'CF-002');});
test('same section name never crosses guide boundaries',()=>{assert.deepEqual(affectedBy(items,'Guía A','Sección 1').map(i=>i.code),['CF-001']); assert.deepEqual(affectedBy(items,'Guía A','Otra'),[]); assert.deepEqual(affectedBy(items,''),[]);});
test('review queues keep missing approval distinct from pending approval',()=>{assert.equal(reviewMatches(items[0],'pending'),true); assert.equal(reviewMatches(items[1],'pending'),false); assert.equal(reviewMatches(items[1],'unspecified'),true); assert.equal(reviewMatches(items[1],'versions'),false);});
test('missing or unrecognized technical reports are never green',()=>{assert.equal(technicalLabel(null),'Sin comprobar'); assert.equal(technicalLabel({status:'approved'}),'Sin comprobar'); assert.equal(technicalLabel({status:'OK'}),'Correcto');});
test('filtering and review never mutate canonical metadata',()=>{const before=JSON.stringify(items); filterItems(items,{query:'garantia'}); affectedBy(items,'Guía A'); items.forEach(i=>reviewMatches(i,'metadata')); assert.equal(JSON.stringify(items),before);});
