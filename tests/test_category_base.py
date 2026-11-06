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
    def test_registry_has_two_available_categories_and_three_preparations(self):
        categories = yaml.safe_load((ROOT / '_data/categories.yml').read_text())
        self.assertEqual(len(categories), 5)
        self.assertEqual(len({c['id'] for c in categories}), 5)
        self.assertEqual(len({c['url'] for c in categories}), 5)
        self.assertEqual([c['id'] for c in categories if c['status'] == 'available'], ['financiamiento-reembolsable', 'donacion'])
        self.assertEqual([r['name'] for r in categories[0]['roles']], ['Promotores', 'Inversores', 'Colaboradores'])
        donation = next(c for c in categories if c['id'] == 'donacion')
        self.assertEqual(donation['status'], 'available')
        self.assertEqual([r['name'] for r in donation['roles']], ['Promotores', 'Donantes', 'Colaboradores'])
        self.assertEqual([r['url'] for r in donation['roles']], [
            '/donacion/promotores/', '/donacion/donantes/', '/donacion/colaboradores/',
        ])
        self.assertNotIn('section_layout', donation['roles'][2])
        for category in categories[2:]:
            self.assertEqual(category['status'], 'preparation')
            self.assertEqual(category['roles'], [])

    def test_donation_publication_keeps_editorial_review_pending(self):
        config, _, _, pages, topics = inventory(ROOT)
        self.assertEqual(len(pages), 60)
        self.assertEqual(len(topics), 40)
        self.assertNotIn('ideas/donacion', config['exclude'])
        for record in pages.values():
            self.assertEqual(record['meta']['editorial_status'], 'pending_review')
            self.assertIs(record['meta']['reviewed'], False)

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
