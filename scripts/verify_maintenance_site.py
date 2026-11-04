#!/usr/bin/env python3
"""Audit generated routes read-only; store evidence outside Jekyll output."""
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



def audit_verified_tiktok(site, config, sharing):
    """Comprueba que el reproductor/ancla y los enlaces existen en el HTML real."""
    report = sharing.get("verified_tiktok")
    if not report:
        return {"checked": 0, "errors": []}
    origin = config['url'].rstrip('/')
    base = config.get('baseurl', '').rstrip('/')
    errors = []
    observed_primary = observed_related = 0
    for ficha in sharing.get("items", []):
        assets = [asset for piece in ficha.get("marketing_pieces", [])
                  for asset in piece.get("assets", [])
                  if asset.get("provider") == "tiktok"]
        if not assets:
            continue
        canonical = ficha["canonical_url"]
        route = urlsplit(canonical).path
        if not canonical.startswith(origin + base + '/') or not route.startswith(base + '/'):
            errors.append(f'{ficha["code"]}: URL canónica inesperada')
            continue
        route = route[len(base):].lstrip('/')
        path = site / route / 'index.html'
        if not path.is_file():
            errors.append(f'{ficha["code"]}: no se generó la ficha')
            continue
        html = path.read_text(encoding='utf-8')
        for asset in assets:
            if not asset.get("original_url"):
                errors.append(f'{ficha["code"]}/{asset["id"]}: sin enlace original')
                continue
            if asset.get("media_url"):
                anchor = 'id="media-' + asset["id"] + '"'
                player = '/player/v1/' + str(asset.get("video_id"))
                if anchor not in html:
                    errors.append(f'{ficha["code"]}/{asset["id"]}: falta ancla multimedia')
                if player not in html:
                    errors.append(f'{ficha["code"]}/{asset["id"]}: falta iframe de TikTok')
                observed_primary += 1
            else:
                if '/@iskay.app/video/' + str(asset.get("video_id")) not in html:
                    errors.append(f'{ficha["code"]}/{asset["id"]}: falta enlace complementario')
                observed_related += 1
    if observed_primary != report.get("principal") or observed_related != report.get("complementaria"):
        errors.append("El total multimedia del HTML no coincide con los enlaces verificados")
    return {"checked": observed_primary + observed_related, "principal": observed_primary,
            "complementaria": observed_related, "errors": errors}


def main():
    site = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / '_site')
    config = yaml.safe_load((ROOT / '_config.yml').read_text(encoding='utf-8'))
    data = json.loads((site / 'mantenimiento/control_catalog.json').read_text(encoding='utf-8'))
    result = audit(site, config, data)
    sharing = json.loads((site / 'mantenimiento/share_catalog.json').read_text(encoding='utf-8'))
    result["tiktok"] = audit_verified_tiktok(site, config, sharing)
    # The container-generated site is read-only to this runner. Keep evidence in
    # the runner-owned artifact directory rather than changing ownership or files.
    artifacts = ROOT / 'ui-artifacts'
    artifacts.mkdir(exist_ok=True)
    (artifacts / 'maintenance-route-audit.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    if result["tiktok"]["errors"]:
        raise SystemExit("Falta multimedia TikTok en las fichas: " + "; ".join(result["tiktok"]["errors"]))
    if result['missing_routes'] or result['unreachable_topics'] or not result['unique_codes'] or not result['unique_routes']:
        raise SystemExit('La publicación contiene rutas duplicadas, ausentes o fichas sin acceso desde la portada.')


if __name__ == '__main__':
    main()
