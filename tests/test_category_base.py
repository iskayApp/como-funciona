"""Review snapshot: preserve FR sources and the verified shared components."""
from pathlib import Path
import subprocess
import sys
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_donation_navigation import inventory


class CategoryBaseTests(unittest.TestCase):
    def test_registry_has_four_available_categories_and_one_preparation(self):
        categories = yaml.safe_load((ROOT / '_data/categories.yml').read_text())
        self.assertEqual(len(categories), 5)
        self.assertEqual(len({c['id'] for c in categories}), 5)
        self.assertEqual(len({c['url'] for c in categories}), 5)
        self.assertEqual([c['id'] for c in categories if c['status'] == 'available'], [
            'financiamiento-reembolsable', 'donacion', 'recompensa', 'precompra',
        ])
        self.assertEqual([r['name'] for r in categories[0]['roles']], ['Promotores', 'Inversores', 'Colaboradores'])
        donation = next(c for c in categories if c['id'] == 'donacion')
        self.assertEqual(donation['status'], 'available')
        self.assertEqual([r['name'] for r in donation['roles']], ['Promotores', 'Donantes', 'Colaboradores'])
        self.assertEqual([r['url'] for r in donation['roles']], [
            '/donacion/promotores/', '/donacion/donantes/', '/donacion/colaboradores/',
        ])
        self.assertNotIn('section_layout', donation['roles'][2])
        reward = next(c for c in categories if c['id'] == 'recompensa')
        self.assertEqual(reward['status'], 'available')
        self.assertEqual([r['name'] for r in reward['roles']], [
            'Promotores', 'Contribuyentes', 'Colaboradores',
        ])
        precompra = next(c for c in categories if c['id'] == 'precompra')
        self.assertEqual(precompra['status'], 'available')
        self.assertEqual([r['name'] for r in precompra['roles']], [
            'Promotores', 'Precompradores', 'Colaboradores',
        ])
        self.assertEqual([r['url'] for r in precompra['roles']], [
            '/precompra/promotores/', '/precompra/precompradores/', '/precompra/colaboradores/',
        ])
        preparation = [c for c in categories if c['status'] == 'preparation']
        self.assertEqual([c['id'] for c in preparation], ['inversion-en-acciones'])
        self.assertEqual(preparation[0]['roles'], [])

    def test_donation_publication_keeps_editorial_review_pending(self):
        config, _, _, pages, topics = inventory(ROOT)
        self.assertEqual(len(pages), 60)
        self.assertEqual(len(topics), 40)
        self.assertNotIn('ideas/donacion', config['exclude'])
        for record in pages.values():
            self.assertEqual(record['meta']['editorial_status'], 'pending_review')
            self.assertIs(record['meta']['reviewed'], False)

    def test_reward_53_topics_review_states_and_primary_sources(self):
        from collections import Counter
        root = ROOT / 'ideas/recompensa'
        records = []
        for source in sorted(root.rglob('cf-rec-*.md')):
            raw = source.read_text(encoding='utf-8')
            self.assertTrue(raw.startswith('---'), source)
            meta = yaml.safe_load(raw.split('---', 2)[1])
            records.append(meta)
        self.assertEqual(len(records), 53)
        self.assertEqual(Counter(row['role'] for row in records), {
            'Promotores': 30, 'Contribuyentes': 14, 'Colaboradores': 9,
        })
        self.assertEqual(len({row['stage_id'] for row in records}), 18)
        self.assertEqual(len({row['code'] for row in records}), 53)
        self.assertEqual(len({row['permalink'] for row in records}), 53)
        refs = [code for row in records for code in row['classification_refs']]
        self.assertEqual(Counter(refs), Counter(
            f'CL-REC-{i:03}' for i in range(1, 114)
        ))
        flagged = {row['code'] for row in records if row['pending_implementation']}
        self.assertEqual(flagged, {
            'CF-REC-PRO-011', 'CF-REC-PRO-012', 'CF-REC-PRO-013',
            'CF-REC-PRO-014', 'CF-REC-CON-004',
        })
        for row in records:
            self.assertEqual(row['status'], 'published')
            self.assertTrue(row['published'])
            self.assertEqual(row['editorial_status'], 'pending_review')
            self.assertIs(row['reviewed'], False)
            self.assertEqual(row['media'], [])
            self.assertEqual(row['marketing_pieces'], [])
            self.assertEqual(row['source_checked_on'], '2026-11-10')
            self.assertTrue(row['permalink'].startswith('/recompensa/'))
        config = yaml.safe_load((ROOT / '_config.yml').read_text())
        self.assertNotIn('ideas/recompensa', config['exclude'])

    def test_home_is_generic_and_keeps_existing_search_and_guidance(self):
        home = (ROOT / 'index.md').read_text()
        meta = yaml.safe_load(home.split('---\n', 2)[1])
        self.assertEqual(meta['title'], 'Cómo funciona')
        self.assertNotIn('fr-role-cards.html', home)
        self.assertNotIn('fr-context.html', home)
        self.assertLess(home.index('id="buscar"'), home.index('include category-cards.html'))
        self.assertLess(home.index('id="orientacion"'), home.index('include category-cards.html'))
        self.assertIn('Sin registro ni datos personales. Tus respuestas no se guardan.', home)

    def test_review_snapshot_preserves_canonical_sources(self):
        # Revisión 2026-11-05: solo formato INV004 y correcciones verificadas de búsqueda/orientación.
        # Centro de mantenimiento renovado el 2026-11-06: las pruebas de interfaz cubren la biblioteca.
        # El corte protege íntegramente FR durante la publicación de otras categorías.
        # Códigos, URL y contenido funcional de las 99 fichas existentes se conservan.
        tree = subprocess.check_output(
            ['git', 'ls-tree', 'HEAD', 'ideas/financiamiento-reembolsable'],
            cwd=ROOT, text=True,
        ).split()[2]
        self.assertEqual(tree, '7fc5a27f8a2ac8acf00a556e7d0c2d790e78e4d7')
        protected = {
            'assets/js/public-search.js': '2184f044adf2daaee453a2a055acf0fcfcb79101',
            'assets/js/guidance.js': '053ea612c0a3b857f68607c00447d7849fa55819',
            'assets/js/maintenance-search.js': '38ee80acf1a103cea316a24b08145fe206b4f71a',
        }
        for path, expected in protected.items():
            actual = subprocess.check_output(['git', 'hash-object', path], cwd=ROOT, text=True).strip()
            self.assertEqual(actual, expected, path)

    def test_availability_requires_real_published_topics_and_landing(self):
        template = (ROOT / '_includes/category-context.html').read_text()
        self.assertIn('entry.published != false', template)
        self.assertIn('cf_category_page and cf_category_topics.size > 0', template)
        self.assertIn("cf_category.status == 'available'", template)


if __name__ == '__main__':
    unittest.main()
