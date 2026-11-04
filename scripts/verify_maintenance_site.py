#!/usr/bin/env python3
"""Audit generated canonical routes and reachability, without external requests."""
from collections import deque
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urljoin, urlsplit
import yaml

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.links = []
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href')
            if href:
                self.links.append(href)


def audit(site, config, data):
    site = site.resolve()
    base = config.get('baseurl', '').rstrip('/')
    origin = config['url'].rstrip('/')
    home = origin + base + '/'

    def target(url):
        parsed = urlsplit(url)
        if parsed.netloc != urlsplit(origin).netloc:
            return None
        route = unquote(parsed.path)
        if base:
            if route != base and not route.startswith(base + '/'):
                return None
            route = route[len(base):]
        path = (site / route.lstrip('/')).resolve()
        if not path.is_relative_to(site):
            return None
        if path.is_dir() or route.endswith('/'):
            path = path / 'index.html'
        return path if path.suffix == '.html' and path.is_file() else None

    visited, queue = set(), deque([home])
    while queue:
        url = queue.popleft()
        path = target(url)
        if path is None or path in visited:
            continue
        visited.add(path)
        for href in Links(path.read_text(encoding='utf-8')).links:
            if href.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                continue
            next_url = urljoin(url, href)
            if target(next_url) not in visited:
                queue.append(next_url)
    missing, orphaned = [], []
    for item in data['items']:
        path = target(item['canonical_url'])
        if path is None:
            missing.append(item['code'])
        elif path not in visited:
            orphaned.append(item['code'])
    codes = [item['code'] for item in data['items']]
    routes = [item['canonical_url'] for item in data['items']]
    return {'checked_at': datetime.now(timezone.utc).isoformat(), 'scope': 'generated_site_routes_only',
            'checked': len(codes), 'missing_routes': missing, 'unreachable_topics': orphaned,
            'unique_codes': len(codes) == len(set(codes)), 'unique_routes': len(routes) == len(set(routes)),
            'reachable': len(codes) - len(missing) - len(orphaned)}


def main():
    site = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / '_site')
    config = yaml.safe_load((ROOT / '_config.yml').read_text(encoding='utf-8'))
    path = site / 'mantenimiento/control_catalog.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    result = audit(site, config, data)
    data['publication_audit'] = result
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    if result['missing_routes'] or result['unreachable_topics'] or not result['unique_codes'] or not result['unique_routes']:
        raise SystemExit('La publicación contiene rutas duplicadas, ausentes o fichas sin acceso desde la portada.')


if __name__ == '__main__':
    main()
