const test = require('node:test');
const assert = require('node:assert/strict');
const {groupItems} = require('../assets/js/maintenance-status.js');
const categories = [
  {id:'a', name:'Categoría A', url:'/a/', roles:[{id:'p',name:'Promotores',url:'/a/p/'},{id:'c',name:'Colaboradores',url:'/a/c/'}]},
  {id:'b', name:'Categoría B', url:'/b/', roles:[{id:'p',name:'Promotores',url:'/b/p/'}]}
];
const item = (code, url, stage = 'Documentación') => ({code,canonical_url:url,stage,stage_order:1,stage_url:url.split('/').slice(0,-2).join('/')+'/'});
test('same section label never merges categories or roles', () => {
  const result = groupItems([item('1','/a/p/docs/one/'), item('2','/a/c/docs/two/'), item('3','/b/p/docs/three/')], categories);
  assert.equal(result.length, 2);
  assert.equal(result[0].roles.length, 2);
  assert.deepEqual(result.flatMap(c=>c.roles.flatMap(r=>r.sections.flatMap(s=>s.items.map(i=>i.code)))), ['1','2','3']);
});
test('distinct section URLs are preserved within one role', () => {
  const result = groupItems([item('1','/a/p/docs/one/'),item('2','/a/p/other/two/')], categories);
  assert.equal(result[0].roles[0].sections.length, 2);
});
test('legacy reports without category and role resolve through canonical URL', () => {
  const result = groupItems([item('1','https://example.test/como-funciona/a/c/docs/one/')], categories, '/como-funciona');
  assert.equal(result[0].id, 'a');
  assert.equal(result[0].roles[0].id, 'c');
});
test('unknown records are shown, not lost or attributed to FR', () => {
  const result = groupItems([{code:'unknown', canonical_url:'/unknown/'}], categories);
  assert.equal(result[0].name, 'Sin categoría identificada');
  assert.equal(result[0].roles[0].name, 'Sin rol identificado');
  assert.equal(result[0].roles[0].sections[0].items[0].code, 'unknown');
});
test('technical grouping does not modify source records or approvals', () => {
  const records = [{...item('1','/a/p/docs/one/'), editorial_status:'pending_review', published:true, reviewed:false}];
  const before = JSON.stringify(records);
  groupItems(records, categories);
  assert.equal(JSON.stringify(records), before);
  assert.deepEqual(groupItems([], categories), []);
});
