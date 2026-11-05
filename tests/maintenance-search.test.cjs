const test = require('node:test');
const assert = require('node:assert/strict');
const { publishedItems, matches } = require('../assets/js/maintenance-search.js');

test('marketing link search excludes unpublished and build-excluded topics', () => {
  const rows = [
    { code: 'AVAILABLE', public_searchable: true },
    { code: 'PREPARATION', public_searchable: false },
    { code: 'UNKNOWN' },
    null
  ];
  const before = JSON.stringify(rows);
  assert.deepEqual(publishedItems(rows).map(row => row.code), ['AVAILABLE']);
  assert.deepEqual(publishedItems(null), []);
  assert.equal(JSON.stringify(rows), before);
});

test('official piece code with category suffix finds its explicit associations', () => {
  const item = {
    code: 'CF-FR-COL-005', title: 'Áreas de colaboración',
    category: 'Financiamiento Reembolsable', role: 'Colaboradores',
    editorial_pieces: [{ code: 'COL-EDU-01', category_code: 'FR', title: 'Criterios técnicos', relation: 'Principal' }]
  };
  assert.equal(matches(item, 'COL-EDU-01 (FR)', '', ''), true);
  assert.equal(matches(item, 'criterios tecnicos', '', ''), true);
  assert.equal(matches(item, 'COL-EDU-01 (FR)', '', 'Inversores'), false);
  assert.equal(matches(item, 'COL-EDU-02 (FR)', '', ''), false);
  const published = { ...item, editorial_pieces: [], marketing_pieces: item.editorial_pieces };
  assert.equal(matches(published, 'COL-EDU-01 (FR)', '', ''), true);
});
