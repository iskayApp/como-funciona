"""Check the real Jekyll output against canonical FR metadata, not a duplicate catalog."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
SITE = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / '_site')
CONFIG = yaml.safe_load((ROOT / '_config.yml').read_text())
BASE = CONFIG.get('baseurl', '').rstrip('/')
FR = '/financiamiento-reembolsable/'
ROLES = {'promotores': (33, 6), 'inversores': (37, 7), 'colaboradores': (29, 8)}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.nodes = []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        self.nodes.append((tag, dict(attributes)))

    def matching(self, tag=None, cls=None, attr=None):
        return [a for t, a in self.nodes if (not tag or t == tag)
                and (not cls or cls in a.get('class', '').split())
                and (not attr or attr in a)]


def output(route):
    path = unquote(urlsplit(route).path)
    if BASE and (path == BASE or path.startswith(BASE + '/')):
        path = path[len(BASE):]
    target = SITE / path.lstrip('/')
    return target / 'index.html' if path.endswith('/') or not path else target


def read(route):
    target = output(route)
    assert target.is_file(), f'Missing generated page: {route}'
    text = target.read_text(encoding='utf-8')
    assert '{{' not in text and '{%' not in text, f'Unrendered Liquid: {route}'
    return text, Page(text)


def main():
    canonical = {}
    for source in (ROOT / 'ideas/financiamiento-reembolsable').rglob('*.md'):
        raw = source.read_text(encoding='utf-8')
        if raw.startswith('---\n'):
            meta = yaml.safe_load(raw.split('---\n', 2)[1]) or {}
            if meta.get('code'):
                canonical[meta['permalink']] = meta
    assert len(canonical) == 99
    pending = 0
    for route, meta in canonical.items():
        text, page = read(route)
        assert len(page.matching('nav', cls='fr-role-tabs')) == 1, route
        assert len(page.matching('details', cls='fr-menu')) == 1, route
        assert len(page.matching('details', cls='fr-jump')) == 1, route
        assert len(page.matching('link', attr='rel')) >= 3, route
        assert any(a.get('name') == 'robots' and 'noindex' in a.get('content', '')
                   for a in page.matching('meta')), route
        if meta.get('editorial_status') == 'pending_review':
            assert 'Pendiente de revisión editorial.' in text, route
            pending += 1
        for a in page.matching('a'):
            href = a.get('href', '')
            if href.startswith(BASE + FR):
                assert output(href).exists(), f'Broken FR link: {route} -> {href}'
    assert pending == 59, pending
    for slug, (count, sections) in ROLES.items():
        route = FR + slug + '/'
        _, page = read(route)
        links = page.matching('a', attr='data-fr-topic')
        expected = {BASE + url for url in canonical if url.startswith(route)}
        actual = [link['href'] for link in links]
        assert len(actual) == count, (slug, len(actual), count)
        assert set(actual) == expected and len(set(actual)) == count, slug
        groups = page.matching('details', cls='fr-section')
        assert len(groups) == sections, (slug, len(groups), sections)
        if slug == 'colaboradores':
            assert Counter(a['data-section-kind'] for a in groups) == {'common': 4, 'area': 4}
    for route in ('/', FR):
        _, page = read(route)
        assert len(page.matching('a', cls='fr-role-card')) == 3, route
    print('PASS: 99 canonical pages; 3 uniform role hubs; 21 sections; 59 review notices; all generated FR links resolve.')


if __name__ == '__main__':
    main()
