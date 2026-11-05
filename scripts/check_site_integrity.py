#!/usr/bin/env python3
"""Validate every rendered page, local destination and fragment before publishing.

External providers are counted, not certified by this offline audit. The check
works with any category/role and also rejects rendered private/draft topics.
"""
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urljoin, urlsplit
import yaml

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids, self.references, self.aria, self.headings = [], [], [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.headings.append(tag)
        for key in ('href', 'src', 'poster'):
            if attrs.get(key):
                self.references.append((tag, key, attrs[key]))
        for key in ('aria-labelledby', 'aria-describedby'):
            if attrs.get(key):
                self.aria.extend(attrs[key].split())


def target_for(site, base, url):
    path = unquote(urlsplit(url).path)
    if base and not (path == base or path.startswith(base + '/')):
        return None
    path = path[len(base):] if base else path
    target = site / path.lstrip('/')
    if path.endswith('/') or not path:
        target /= 'index.html'
    elif target.is_dir():
        target /= 'index.html'
    return target


def audit(site, root=ROOT):
    site, root = Path(site).resolve(), Path(root).resolve()
    config = yaml.safe_load((root / '_config.yml').read_text()) or {}
    origin = str(config.get('url', '')).rstrip('/')
    base = str(config.get('baseurl', '')).rstrip('/')
    host = urlsplit(origin).netloc
    registry_path = root / '_data/categories.yml'
    categories = yaml.safe_load(registry_path.read_text()) if registry_path.exists() else []
    pages = {p: Page(p.read_text(encoding='utf-8')) for p in site.rglob('*.html')}
    errors, external = [], set()
    links, anchors = 0, 0
    for path, page in sorted(pages.items()):
        relative = path.relative_to(site).as_posix()
        current = origin + base + '/' + relative
        duplicates = [key for key, count in Counter(page.ids).items() if count > 1]
        if duplicates:
            errors.append(f'{relative}: duplicate IDs {duplicates}')
        for ref in page.aria:
            if ref not in page.ids:
                errors.append(f'{relative}: missing ARIA target #{ref}')
        if page.headings.count('h1') != 1:
            errors.append(f'{relative}: expected one h1, found {page.headings.count("h1")}')
        for tag, key, ref in page.references:
            parsed = urlsplit(ref)
            if parsed.scheme and parsed.scheme not in ('http', 'https'):
                continue
            absolute = urljoin(current, ref)
            parsed = urlsplit(absolute)
            if parsed.netloc != host:
                external.add(absolute)
                continue
            target = target_for(site, base, absolute)
            if target is None:
                external.add(absolute)
                continue
            links += 1
            if not target.is_file():
                errors.append(f'{relative}: missing local {key} {ref}')
                continue
            if parsed.fragment and target in pages:
                anchors += 1
                if unquote(parsed.fragment) not in pages[target].ids:
                    errors.append(f'{relative}: missing fragment {ref}')
    # Jekyll understands published:false, but visibility/status are application
    # metadata. Reject accidental rendered drafts even if menus hide them.
    for path in (root / 'ideas').rglob('*.md'):
        raw = path.read_text(encoding='utf-8')
        if not raw.startswith('---\n'):
            continue
        meta = yaml.safe_load(raw.split('---\n', 2)[1]) or {}
        category = next((c for c in categories if c.get('name') == meta.get('category')), None)
        restricted = (meta.get('published') is False or meta.get('visibility') == 'private'
                      or meta.get('status') in ('draft', 'review', 'archived')
                      or (category is not None and category.get('status') != 'available'))
        if not meta.get('code') or not restricted or not meta.get('permalink'):
            continue
        target = target_for(site, base, origin + base + meta['permalink'])
        if target is not None and target.exists():
            errors.append(f'{meta["code"]}: restricted topic was rendered at {meta["permalink"]}')
    return {'scope': 'rendered_site_offline', 'pages': len(pages),
            'local_references': links, 'fragments': anchors,
            'external_destinations_not_checked': len(external), 'errors': sorted(set(errors))}


def main():
    result = audit(sys.argv[1] if len(sys.argv) > 1 else ROOT / '_site')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result['pages'] or result['errors']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
