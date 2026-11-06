const test = require('node:test');
const assert = require('node:assert/strict');
const C = require('../assets/js/maintenance-core.js');
const revision = 'a'.repeat(40), now = Date.parse('2026-11-06T12:00:00Z');
const current = () => ({revision,generated_at:'2026-11-06T11:00:00Z',items:[]});

test('technical success requires a current timestamp and exact valid revision', () => {
  assert.equal(C.reportState(current(), revision, now).current, true);
  assert.equal(C.reportState({...current(), revision:'b'.repeat(40)}, revision, now).kind, 'mismatch');
  assert.equal(C.reportState({...current(), generated_at:'2026-11-01T11:00:00Z'}, revision, now).kind, 'stale');
  assert.equal(C.reportState({...current(), generated_at:'2026-11-07T11:00:00Z'}, revision, now).kind, 'unknown');
  assert.equal(C.reportState({...current(), revision:null}, revision, now).current, false);
  assert.equal(C.reportState({...current(), revision:'invalid'}, 'invalid', now).current, false);
  assert.equal(C.reportState(null, revision, now).current, false);
});

test('empty, failed and historic inventories are distinct from a verified zero', () => {
  const report = {...current(),services:{tiktok:{status:'OK'}},tiktok_inventory:{complete:true,videos:[]}};
  assert.equal(C.inventoryState(report, revision, now).known, true);
  for (const incomplete of [
    {...report,tiktok_inventory:{videos:[]}},
    {...report,services:{tiktok:{status:'SIN COMPROBAR'}}},
    {...report,revision:'b'.repeat(40)},
    null,
  ]) {
    assert.equal(C.inventoryState(incomplete, revision, now).known, false);
    assert.equal(C.inventoryState(incomplete, revision, now).label, 'Pendientes sin comprobar');
  }
});

test('inventories retain historical unlinked resources without claiming completeness', () => {
  const report={...current(),tiktok_inventory:{videos:[{status:'SIN VINCULAR',video_id:'1'}]},services:{tiktok:{status:'SIN COMPROBAR'}}};
  assert.equal(C.inventoryState(report,revision,now).pending.length,1);
  assert.equal(C.inventoryState(report,revision,now).known,false);
});

test('filtered summaries do not borrow global approvals or totals', () => {
  const rows=[{editorial_status:'approved',video_count:1},{editorial_status:'pending_review',video_count:0},{editorial_status:'unspecified',video_count:0}];
  assert.deepEqual(C.summarize(rows.slice(0,1)),{total:1,approved:1,pending:0,unspecified:0,withVideo:1,noVideo:0,metadata:0,unverified:0});
  assert.equal(C.summarize(rows).unspecified,1);
});

test('same video across multiple fichas is one resource and retains both placements', () => {
  const rows=[
    {code:'A',title:'Primera',content_version:1,media:[{id:'a',provider:'tiktok',video_id:'123',derived_from_version:1}]},
    {code:'B',title:'Segunda',content_version:null,media:[{id:'b',provider:'tiktok',video_id:'123',derived_from_version:null}]},
  ];
  const before=JSON.stringify(rows), result=C.uniqueResources(rows);
  assert.equal(result.length,1); assert.equal(result[0].placements.length,2);
  assert.equal(result[0].placements[1].derived_from_version,null);
  assert.equal(JSON.stringify(rows),before);
});

test('missing provenance is a queue independent of known version mismatches', () => {
  const item={metadata_gaps:['guide_version'],unverified_asset_ids:['video'],stale_asset_ids:[],video_count:1};
  assert.equal(C.reviewMatches(item,'gap:guide_version'),true);
  assert.equal(C.reviewMatches(item,'gap:content_version'),false);
  assert.equal(C.reviewMatches(item,'unverified'),true);
  assert.equal(C.reviewMatches(item,'media'),false);
  assert.equal(C.reviewMatches(item,'no-video'),false);
});

test('CSV escapes quotes and prevents spreadsheet formula execution', () => {
  const text=C.csv([['Código','Texto'],['=1+1','Dice "hola"'],['  @SUM(A1)','Primera\nSegunda'],['\tunsafe','Normal']]);
  assert.ok(text.startsWith('\uFEFF'));
  assert.ok(text.includes('"\'=1+1"'));
  assert.ok(text.includes('"Dice ""hola"""'));
  assert.ok(text.includes('"\'  @SUM(A1)"'));
  assert.ok(text.includes('"\'\tunsafe"'));
  assert.ok(text.includes('"Primera\nSegunda"'));
});

test('maintenance links reject active protocols, credentials and insecure external origins', () => {
  for(const url of ['javascript:alert(1)','data:text/html,Hello','https://user:secret@example.org','http://example.org'])assert.equal(C.safeURL(url,'https://site.example/'), '');
  assert.equal(C.safeURL('/guide','http://127.0.0.1:4000/'),'http://127.0.0.1:4000/guide');
});
