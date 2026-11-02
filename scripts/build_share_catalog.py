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
        }

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
        catalog.append(entry)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_fichas": len(catalog),
        "total_media": sum(len(entry["media"]) for entry in catalog),
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
