#!/usr/bin/env python3
"""Read-only public projection for the four maintenance views.

Canonical front matter owns content/version/approval. share_catalog owns resource
and marketing associations. This projection never exports bodies, private drafts,
free-form notes or arbitrary metadata, and never changes either source.
"""
from collections import Counter
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import quote, urlsplit
import yaml
from build_share_catalog import frontmatter

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/iskayApp/como-funciona'
PHASES = {'classified', 'organized', 'identified', 'developed'}
EDITORIAL = {'approved', 'pending_review', 'draft', 'changes_requested'}


def text(value):
    return value.strip() if isinstance(value, str) else ''


def scalar(value):
    if isinstance(value, bool) or value is None:
        return None
    return value if isinstance(value, (str, int, float)) else None


def stamp(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return text(value)


def safe_url(value):
    value = text(value)
    try:
        parts = urlsplit(value)
    except ValueError:
        return None
    return value if parts.scheme == 'https' and parts.netloc and not parts.username and not parts.password else None


def excluded(path, config):
    return any(path == str(rule).rstrip('/') or path.startswith(str(rule).rstrip('/') + '/')
               for rule in config.get('exclude', []))


def is_public(meta, path, config):
    return (not excluded(path, config) and meta.get('published') is not False
            and meta.get('visibility') != 'private'
            and meta.get('status') not in ('draft', 'review', 'archived'))


def public_route(value):
    return (isinstance(value, str) and value.startswith('/') and not value.startswith('//')
            and '..' not in value.split('/') and not any(c in value for c in ('?', '#', '\\')))


def source_details(meta):
    raw = text(meta.get('source'))
    parts = re.split(r'\s+[—–]\s+', raw, maxsplit=1)
    label = parts[0] if parts else ''
    sections = [s.strip().rstrip('.') for s in parts[1].split(';') if s.strip()] if len(parts) > 1 else []
    version = text(meta.get('guide_version'))
    known = bool(version) and not any(s in version.casefold() for s in ('no identificada', 'sin identificar', 'sin versión'))
    return {'label': label, 'sections': sections, 'reference': raw,
            'version': version or None, 'version_identified': known}


def preparation_rows(registry):
    rows = []
    used = set()
    for raw in registry.get('preparation', []):
        if raw.get('public') is not True:
            continue
        code = text(raw.get('code'))
        if not code or code in used or raw.get('phase') not in PHASES:
            raise ValueError('Referencia de preparación duplicada o incompleta')
        used.add(code)
        digest = text(raw.get('content_sha256'))
        if digest and not re.fullmatch(r'[a-f0-9]{64}', digest):
            raise ValueError('content_sha256 debe contener el SHA-256 del cuerpo canónico')
        rows.append({'code': code, 'title': text(raw.get('title')), 'category_id': text(raw.get('category_id')),
                     'role_id': text(raw.get('role_id')), 'phase': raw['phase'],
                     'version': scalar(raw.get('version')), 'content_sha256': digest or None,
                     'reference_url': safe_url(raw.get('reference_url')), 'updated_at': stamp(raw.get('updated_at'))})
    return rows


def comparison(published_version, digest, prep):
    if not prep:
        return 'no_reference'
    if prep.get('content_sha256'):
        return 'same_content' if prep['content_sha256'] == digest else 'different_content'
    if prep.get('version') is not None and published_version is not None:
        return 'same_version_unverified' if str(prep['version']) == str(published_version) else 'different_version'
    return 'unverified'


def build_control(root=ROOT, revision=None):
    config = yaml.safe_load((root / '_config.yml').read_text(encoding='utf-8'))
    categories = yaml.safe_load((root / '_data/categories.yml').read_text(encoding='utf-8'))
    registry_path = root / '_data/maintenance-public.yml'
    registry = yaml.safe_load(registry_path.read_text(encoding='utf-8')) if registry_path.exists() else {}
    registry = registry or {}
    catalog = json.loads((root / 'mantenimiento/share_catalog.json').read_text(encoding='utf-8'))
    shared = {entry['code']: entry for entry in catalog.get('items', [])}
    preparation = preparation_rows(registry)
    prep_by_code = {row['code']: row for row in preparation}
    revision = revision or os.environ.get('GITHUB_SHA', '')
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        try:
            revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
        except (subprocess.CalledProcessError, OSError):
            revision = ''
    items = []
    codes, routes = set(), set()
    for path in sorted((root / 'ideas').rglob('*.md')):
        relative = path.relative_to(root).as_posix()
        meta, body = frontmatter(path.read_text(encoding='utf-8'))
        code = text(meta.get('code'))
        if not code or not is_public(meta, relative, config):
            continue
        route = meta.get('permalink')
        if not public_route(route):
            raise ValueError(f'{relative}: permalink inválido')
        if code in codes or route in routes:
            raise ValueError(f'{relative}: código o permalink duplicado')
        codes.add(code)
        routes.add(route)
        category = next((c for c in categories if route.startswith(c['url'])), None)
        role = next((r for r in (category or {}).get('roles', []) if route.startswith(r['url'])), None)
        entry = shared.get(code)
        if not entry or not entry.get('public_searchable'):
            raise ValueError(f'{code}: ficha pública ausente del catálogo común')
        if not category or not role:
            raise ValueError(f'{code}: categoría o rol no registrados')
        source = source_details(meta)
        editorial = meta.get('editorial_status') if meta.get('editorial_status') in EDITORIAL else 'unspecified'
        version = scalar(meta.get('content_version'))
        digest = hashlib.sha256(body.encode('utf-8')).hexdigest()
        prep = prep_by_code.get(code)
        assets = list(entry.get('media', [])) + list(entry.get('distribution', []))
        stale = [a['id'] for a in assets if a.get('derived_from_version') is not None
                 and version is not None and str(a['derived_from_version']) != str(version)]
        missing = []
        if editorial == 'unspecified': missing.append('editorial_state')
        if not source['label']: missing.append('functional_source')
        if not source['sections']: missing.append('source_section')
        if not source['version_identified']: missing.append('guide_version')
        if version is None: missing.append('content_version')
        items.append({
            'code': code, 'title': text(meta.get('title')) or code,
            'category_id': category['id'], 'category': category['name'],
            'role_id': role['id'], 'role': role['name'], 'stage': text(meta.get('stage')),
            'stage_url': text(meta.get('stage_url')), 'canonical_url': entry['canonical_url'],
            'source': source, 'source_file_url': f'{REPO}/blob/{revision or "main"}/{quote(relative)}',
            'editorial_status': editorial, 'reviewed_at': stamp(meta.get('reviewed')),
            'publication_status': 'test_published' if config.get('noindex') else 'published',
            'content_version': version, 'content_sha256': digest,
            'preparation': prep, 'version_comparison': comparison(version, digest, prep),
            'metadata_gaps': missing, 'stale_asset_ids': stale,
            'embedded_count': len(entry.get('media', [])),
            'distribution_count': len(entry.get('distribution', [])),
            'marketing_codes': [p['code'] for p in entry.get('marketing_pieces', [])],
            'resource_ids': [a['id'] for a in assets],
        })
    new_preparation = [p for p in preparation if p['code'] not in codes]
    category_rows = []
    for category in categories:
        matches = [i for i in items if i['category_id'] == category['id']]
        category_rows.append({'id': category['id'], 'name': category['name'], 'status': category['status'],
                              'published_count': len(matches),
                              'roles': [{'id': r['id'], 'name': r['name'], 'published_count': sum(i['role_id'] == r['id'] for i in matches)} for r in category.get('roles', [])]})
    controls = [{'category_id': text(c.get('category_id')), 'title': text(c.get('title')), 'url': safe_url(c.get('url'))}
                for c in registry.get('editorial_controls', []) if safe_url(c.get('url'))]
    changes = []
    for change in registry.get('guide_changes', []):
        if change.get('public') is not True:
            continue
        source_label, section = text(change.get('source_label')), text(change.get('section'))
        affected = [i['code'] for i in items if source_label and i['source']['label'] == source_label
                    and (not section or section in i['source']['sections'])]
        changes.append({'id': text(change.get('id')), 'title': text(change.get('title')),
                        'source_label': source_label, 'section': section, 'affected_codes': affected,
                        'reference_url': safe_url(change.get('reference_url')), 'recorded_at': stamp(change.get('recorded_at'))})
    return {'schema_version': 1, 'generated_at': datetime.now(timezone.utc).isoformat(),
            'revision': revision or None, 'revision_url': f'{REPO}/commit/{revision}' if revision else None,
            'read_only': True, 'scope': 'public_metadata_only',
            'summary': {'published': len(items), 'editorial': dict(Counter(i['editorial_status'] for i in items)),
                        'with_metadata_gaps': sum(bool(i['metadata_gaps']) for i in items),
                        'with_stale_assets': sum(bool(i['stale_asset_ids']) for i in items),
                        'preparation_references': len(preparation)},
            'categories': category_rows, 'items': items, 'preparation': new_preparation,
            'editorial_controls': controls, 'guide_changes': changes,
            'limitations': {'drive_sync': False, 'private_drafts_included': False, 'live_editorial_controls': False}}


def main():
    data = build_control()
    output = ROOT / 'mantenimiento/control_catalog.json'
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Control público generado:', json.dumps(data['summary'], ensure_ascii=False))


if __name__ == '__main__':
    main()
