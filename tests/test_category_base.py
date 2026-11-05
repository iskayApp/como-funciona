"""Review snapshot: preserve FR sources and the verified shared components."""
from pathlib import Path
import subprocess
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class CategoryBaseTests(unittest.TestCase):
    def test_registry_has_one_available_category_and_four_preparations(self):
        categories = yaml.safe_load((ROOT / '_data/categories.yml').read_text())
        self.assertEqual(len(categories), 5)
        self.assertEqual(len({c['id'] for c in categories}), 5)
        self.assertEqual(len({c['url'] for c in categories}), 5)
        self.assertEqual([c['id'] for c in categories if c['status'] == 'available'], ['financiamiento-reembolsable'])
        self.assertEqual([r['name'] for r in categories[0]['roles']], ['Promotores', 'Inversores', 'Colaboradores'])
        for category in categories[1:]:
            self.assertEqual(category['status'], 'preparation')
            self.assertEqual(category['roles'], [])

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
        # Las pruebas de comportamiento cubren cada corrección; códigos, URL y palabras se conservan.
        tree = subprocess.check_output(['git', 'ls-tree', 'HEAD', 'ideas'], cwd=ROOT, text=True).split()[2]
        self.assertEqual(tree, '89d23ea6b5ba9548af66fe5eadf0aafdcb681291')
        protected = {
            'assets/js/public-search.js': '2184f044adf2daaee453a2a055acf0fcfcb79101',
            'assets/js/guidance.js': '053ea612c0a3b857f68607c00447d7849fa55819',
            'assets/js/maintenance-search.js': 'cf5df58a8737a8570d8aa6f609f4c4c6168c661c',
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
