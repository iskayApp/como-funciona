#!/usr/bin/env python3
"""Construye y comprueba el catálogo de enlaces de Cómo funciona.

No depende de nombres de roles ni de categorías: usa metadatos por ficha.
Requiere PyYAML (ya instalado por el flujo de GitHub Pages).
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
IDEAS = ROOT / "ideas"
OUTPUT = ROOT / "mantenimiento" / "share_catalog.json"


def frontmatter(text):
    if not text.startswith("---\n"):
        return {}, text
    marker = text.find("\n---\n", 4)
    if marker < 0:
        return {}, text
    return yaml.safe_load(text[4:marker]) or {}, text[marker + 5:]


def slugify(value):
    # IDs de multimedia usan el subconjunto seguro ASCII: letras, números y guiones.
    return re.sub(r"[^a-z0-9-]+", "-", str(value).lower()).strip("-")


def public_url(config, path):
    if not path.startswith("/"):
        raise ValueError("La ruta interna debe comenzar con /")
    return config["url"].rstrip("/") + config.get("baseurl", "").rstrip("/") + path


def valid_http_url(value):
    if not isinstance(value, str):
        return False
    p = urlsplit(value.strip())
    return p.scheme in ("https", "http") and bool(p.netloc)


def original_url(media, config):
    # Prioridad a la publicación original declarada explícitamente.
    original = media.get("original_url") or media.get("share_url") or media.get("url")
    if valid_http_url(original):
        return original.strip()
    if media.get("provider") == "youtube" and media.get("video_id"):
        return "https://www.youtube.com/watch?v=" + quote(str(media["video_id"]), safe="")
    src = media.get("src")
    if media.get("storage") == "internal" and isinstance(src, str) and src.startswith("/assets/"):
        return public_url(config, src)
    if media.get("storage") == "external" and valid_http_url(src):
        return src.strip()
    return None



def distribution_items(value):
    """Normaliza canales de distribución dict/list sin imponer un rol o proveedor."""
    if not isinstance(value, dict):
        return
    for channel, assets in value.items():
        if channel in ("canonical_url", "source", "version"):
            continue
        if isinstance(assets, dict):
            rows = [assets]
        elif isinstance(assets, list):
            rows = [asset for asset in assets if isinstance(asset, dict)]
        else:
            continue
        for asset in rows:
            provider = asset.get("provider") or asset.get("platform") or channel
            yield str(provider), asset


def visible_marketing_pieces(data, entry, path, errors):
    """Asociación editorial explícita; nunca deduce códigos publicitarios de la ficha."""
    pieces = data.get("marketing_pieces") or []
    if not isinstance(pieces, list):
        errors.append(f"{path}: marketing_pieces debe ser una lista")
        return [], list(entry["media"]) + list(entry["distribution"])

    assets = list(entry["media"]) + list(entry["distribution"])
    by_id = {}
    for asset in assets:
        by_id.setdefault(str(asset["id"]), []).append(asset)

    associations = []
    associated_ids = set()
    seen_codes = set()
    for piece in pieces:
        if not isinstance(piece, dict):
            errors.append(f"{path}: entrada marketing_pieces inválida")
            continue
        if piece.get("status") not in ("approved", "published") or piece.get("visibility") == "private":
            continue
        code = piece.get("code")
        if not isinstance(code, str) or not code.strip():
            errors.append(f"{path}: pieza publicitaria publicada sin código oficial")
            continue
        code = code.strip()
        if code in seen_codes:
            errors.append(f"{path}: código de pieza publicitaria repetido en ficha: {code}")
            continue
        seen_codes.add(code)
        refs = piece.get("asset_ids") or []
        if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
            errors.append(f"{path}: {code} requiere asset_ids como lista de IDs")
            continue
        linked = []
        for ref in dict.fromkeys(refs):
            found = by_id.get(ref, [])
            if len(found) != 1:
                errors.append(
                    f"{path}: {code} referencia asset_id '{ref}' que no identifica "
                    "exactamente un recurso/publicación aprobada de la ficha"
                )
                continue
            linked.append(found[0])
            associated_ids.add(ref)
        associations.append({
            "code": code,
            "category_code": piece.get("category_code"),
            "title": piece.get("title") or code,
            "assets": linked,
        })
    unassigned = [asset for asset in assets if str(asset["id"]) not in associated_ids]
    return associations, unassigned


def build_catalog():
    config = yaml.safe_load((ROOT / "_config.yml").read_text(encoding="utf-8"))
    catalog = []
    errors = []
    warnings = []
    used_codes = set()
    used_urls = set()
    used_media_ids = set()

    for path in sorted(IDEAS.rglob("*.md")):
        data, body = frontmatter(path.read_text(encoding="utf-8"))
        code = data.get("code")
        if not code:
            continue
        permalink = data.get("permalink")
        if not isinstance(permalink, str) or not permalink.startswith("/"):
            errors.append(f"{path}: falta permalink absoluto")
            continue
        if code in used_codes or permalink in used_urls:
            errors.append(f"{path}: código o permalink duplicado")
        used_codes.add(code)
        used_urls.add(permalink)

        canonical = public_url(config, permalink)
        parts = path.relative_to(IDEAS).parts
        entry = {
            "code": code,
            "title": data.get("title"),
            "category": data.get("category") or parts[0],
            "role": data.get("role") or (parts[1] if len(parts) > 1 else None),
            "stage": data.get("stage"),
            "content_version": data.get("content_version"),
            "canonical_url": canonical,
            "media": [],
            "distribution": [],
        }

        referenced_ids = set()
        referenced_videos = set()
        for media in data.get("media") or []:
            if not isinstance(media, dict) or media.get("status") != "approved" or media.get("visibility") == "private":
                continue
            media_id = media.get("id")
            slug = slugify(media_id or "")
            if not media_id or not slug:
                errors.append(f"{path}: multimedia sin id estable")
                continue
            if slug != str(media_id):
                errors.append(f"{path}: id multimedia no seguro para URL: {media_id}")
            if media_id in used_media_ids:
                errors.append(f"{path}: id multimedia duplicado entre fichas: {media_id}")
            used_media_ids.add(media_id)
            anchor = "media-" + slug
            if not re.search(r"""\bid\s*=\s*["']""" + re.escape(anchor) + r"""["']""", body):
                errors.append(f"{path}: falta el ancla #{anchor} en el cuerpo")
            origin = original_url(media, config)
            if not origin:
                warnings.append(f"{code}/{media_id}: sin recurso original enlazable")
            referenced_ids.add(str(media_id))
            if media.get("video_id"):
                referenced_videos.add((str(media.get("provider") or ""), str(media["video_id"])))
            entry["media"].append({
                "id": media_id,
                "type": media.get("type"),
                "title": media.get("title") or media.get("caption") or media_id,
                "provider": media.get("provider") or media.get("storage"),
                "derived_from_version": media.get("derived_from_version"),
                "media_url": canonical + "#" + anchor,
                "original_url": origin,
                "original_available": bool(origin),
            })

        # Las publicaciones derivadas no son anclas dentro de una ficha.
        # Se muestran como piezas vinculadas con URL original, sin inventar media_url.
        seen_distribution = set()
        for provider, asset in distribution_items(data.get("distribution") or {}):
            if asset.get("status") not in ("approved", "published") or asset.get("visibility") == "private":
                continue
            asset_id = asset.get("id") or asset.get("asset_id") or asset.get("video_id")
            if not asset_id:
                warnings.append(f"{code}/{provider}: distribución sin identificador estable")
                continue
            asset_id = str(asset_id)
            video_id = str(asset.get("video_id") or "")
            if asset_id in referenced_ids or (video_id and (provider, video_id) in referenced_videos):
                continue
            duplicate_key = (provider, asset_id)
            if duplicate_key in seen_distribution:
                continue
            seen_distribution.add(duplicate_key)
            origin = original_url({**asset, "provider": provider}, config)
            if not origin:
                warnings.append(f"{code}/{asset_id}: publicación sin URL original verificable")
            entry["distribution"].append({
                "id": asset_id,
                "type": asset.get("type") or "publicacion",
                "title": asset.get("title") or asset.get("caption") or asset_id,
                "provider": provider,
                "derived_from_version": asset.get("derived_from_version"),
                "media_url": None,
                "original_url": origin,
                "original_available": bool(origin),
            })
        # Una pieza de marketing puede asociar varios recursos y varias fichas pueden
        # remitir al mismo código publicitario sin renombrar ninguno de sus IDs.
        marketing_pieces, unassigned_assets = visible_marketing_pieces(data, entry, path, errors)
        entry["marketing_pieces"] = marketing_pieces
        entry["unassigned_assets"] = unassigned_assets
        catalog.append(entry)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_fichas": len(catalog),
        "total_media": sum(len(entry["media"]) for entry in catalog),
        "total_distribution": sum(len(entry["distribution"]) for entry in catalog),
        "total_marketing_pieces": sum(len(entry["marketing_pieces"]) for entry in catalog),
        "total_unassigned_assets": sum(len(entry["unassigned_assets"]) for entry in catalog),
        "items": catalog,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for warning in warnings:
        print("AVISO:", warning)
    for error in errors:
        print("ERROR:", error, file=sys.stderr)
    print(f"Catálogo generado: {len(catalog)} fichas, {output['total_media']} recursos.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(build_catalog())
