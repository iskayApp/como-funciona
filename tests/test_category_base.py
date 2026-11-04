"""Phase 1: general shell, with FR and existing search/guidance protected."""
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

    def test_phase_one_does_not_edit_canonical_sources(self):
        # Canonical content remains frozen during the authorized CF-UX-001 redesign.
        tree = subprocess.check_output(['git', 'ls-tree', 'HEAD', 'ideas'], cwd=ROOT, text=True).split()[2]
        self.assertEqual(tree, 'deee78e1e0402f19730287c9d9bd0ac28d85c75b')
        protected = {
            'assets/js/public-search.js': 'dd728f8be3f2a42f0b7f7879dc5870ccba1a72fa',
            'assets/js/guidance.js': '6afa1f1ab68bfcc139b4e8ade5613e223f232674',
            'assets/js/maintenance-search.js': 'a5f8879c3fdf35ef686ed47ea07b7f874b3c8a76',
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
