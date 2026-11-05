import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('site_integrity', Path(__file__).resolve().parents[1] / 'scripts/check_site_integrity.py')
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class SiteIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '_config.yml').write_text('url: https://example.test\nbaseurl: /ayuda\n')
        self.site = self.root / '_site'
        self.site.mkdir()
        (self.site / 'index.html').write_text('<h1>Ayuda</h1><a href="/ayuda/donacion/donantes/#aporte">Donar</a>')
        self.topic = self.site / 'donacion/donantes/index.html'
        self.topic.parent.mkdir(parents=True)
        self.topic.write_text('<h1>Donantes</h1><h2 id="aporte">Aporte</h2>')

    def test_routes_and_fragments_across_another_category(self):
        result = CHECK.audit(self.site, self.root)
        self.assertEqual(result['pages'], 2)
        self.assertEqual(result['fragments'], 1)
        self.assertEqual(result['errors'], [])

    def test_detects_broken_route_fragment_and_aria_target(self):
        self.topic.write_text('<h1>Donantes</h1><a href="/ayuda/no-existe/">Falta</a><p aria-labelledby="ausente"></p>')
        result = CHECK.audit(self.site, self.root)
        self.assertEqual(len(result['errors']), 3)
        self.assertTrue(any('missing fragment' in e for e in result['errors']))
        self.assertTrue(any('missing ARIA' in e for e in result['errors']))

    def test_detects_duplicate_ids_and_restricted_rendered_topic(self):
        self.topic.write_text('<h1>Donantes</h1><h2 id="aporte">Aporte</h2><p id="aporte">Duplicado</p>')
        source = self.root / 'ideas/donacion/donantes.md'
        source.parent.mkdir(parents=True)
        source.write_text('---\ncode: CF-DON-DON-001\nvisibility: private\npermalink: /donacion/donantes/\n---\n')
        result = CHECK.audit(self.site, self.root)
        self.assertTrue(any('duplicate IDs' in e for e in result['errors']))
        self.assertTrue(any('restricted topic' in e for e in result['errors']))

    def test_external_provider_is_counted_not_certified(self):
        self.topic.write_text('<h1>Donantes</h1><h2 id="aporte">Aporte</h2><a href="https://provider.example/video">Vídeo</a>')
        result = CHECK.audit(self.site, self.root)
        self.assertEqual(result['external_destinations_not_checked'], 1)
        self.assertEqual(result['errors'], [])

    def test_category_in_preparation_cannot_be_published_by_removing_an_exclusion(self):
        registry = self.root / '_data/categories.yml'
        registry.parent.mkdir()
        registry.write_text('- name: Donación\n  status: preparation\n')
        source = self.root / 'ideas/donacion/donantes.md'
        source.parent.mkdir(parents=True)
        source.write_text('---\ncode: CF-DON-DON-001\ncategory: Donación\npublished: true\npermalink: /donacion/donantes/\n---\n')
        result = CHECK.audit(self.site, self.root)
        self.assertTrue(any('restricted topic' in e for e in result['errors']))
