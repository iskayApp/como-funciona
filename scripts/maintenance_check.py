#!/usr/bin/env python3
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml

ROOT = Path(__file__).resolve().parents[1]
IDEAS = ROOT / "ideas"
OUT_DIR = ROOT / "mantenimiento"
OUT_FILE = OUT_DIR / "status.json"
BASEURL = "/como-funciona"

RELATIVE_URL_RE = re.compile(r"""\{\{\s*['"]([^'"]+)['"]\s*\|\s*relative_url\s*\}\}""")
MARKDOWN_LINK_RE = re.compile(r"""\[[^\]]*\]\(([^)]+)\)""")

def read_front_matter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5:]
    data = yaml.safe_load(raw) or {}
    return data, body

def normalize_url(value):
    if not value or not isinstance(value, str):
        return None
    value = value.strip()
    if not value:
        return None
    value = value.split("#", 1)[0]
    value = value.split("?", 1)[0]
    if not value:
        return "/"
    if value.startswith(BASEURL + "/"):
        value = value[len(BASEURL):]
    if value != "/" and not value.endswith("/") and not Path(value).suffix:
        value += "/"
    return value

def check_http(url, timeout=10):
    headers = {"User-Agent": "iskay-como-funciona-maintenance/1.0"}
    try:
        req = Request(url, headers=headers, method="HEAD")
        with urlopen(req, timeout=timeout) as r:
            code = getattr(r, "status", 200)
            return 200 <= code < 400, code, None
    except HTTPError as e:
        if e.code in (403, 405):
            try:
                req = Request(url, headers={**headers, "Range": "bytes=0-0"}, method="GET")
                with urlopen(req, timeout=timeout) as r:
                    code = getattr(r, "status", 200)
                    return 200 <= code < 400, code, None
            except Exception as e2:
                return False, getattr(e2, "code", None), str(e2)
        return False, e.code, str(e)
    except (URLError, TimeoutError, OSError) as e:
        return False, None, str(e)

def check_youtube(video_id):
    if not video_id:
        return False, None, "video_id ausente"
    watch = f"https://www.youtube.com/watch?v={video_id}"
    url = "https://www.youtube.com/oembed?url=" + quote(watch, safe="") + "&format=json"
    headers = {"User-Agent": "iskay-como-funciona-maintenance/1.0"}
    try:
        with urlopen(Request(url, headers=headers), timeout=10) as r:
            code = getattr(r, "status", 200)
            return 200 <= code < 400, code, None
    except HTTPError as e:
        return False, e.code, str(e)
    except (URLError, TimeoutError, OSError) as e:
        return False, None, str(e)

def status_rank(status):
    return {"ROTO": 4, "REVISAR": 3, "SIN COMPROBAR": 2, "OK": 1}.get(status, 0)

def worst_status(statuses):
    statuses = [s for s in statuses if s]
    return max(statuses, key=status_rank) if statuses else "OK"

def main():
    pages = []
    permalink_map = {}
    file_map = {}

    for path in sorted(IDEAS.rglob("*.md")):
        data, body = read_front_matter(path)
        if not data:
            continue
        rel = path.relative_to(ROOT).as_posix()
        permalink = normalize_url(data.get("permalink"))
        rec = {"path": rel, "data": data, "body": body}
        pages.append(rec)
        file_map[rel] = rec
        if permalink:
            permalink_map[permalink] = rec

    items = []
    totals = {
        "fichas": 0,
        "recursos": 0,
        "videos_youtube": 0,
        "ok": 0,
        "revisar": 0,
        "rotos": 0,
        "sin_comprobar": 0,
    }

    for rec in pages:
        data, body = rec["data"], rec["body"]
        code = data.get("code")
        if not code:
            continue

        totals["fichas"] += 1
        content_version = data.get("content_version")
        title = data.get("title") or code
        canonical = normalize_url(data.get("permalink"))
        page_statuses = []
        checks = []
        media_rows = []

        if content_version is None:
            checks.append({
                "kind": "version",
                "label": "Versión canónica",
                "status": "REVISAR",
                "detail": "La ficha no tiene content_version."
            })
            page_statuses.append("REVISAR")

        for field in ("prev_url", "next_url", "stage_url"):
            url = normalize_url(data.get(field))
            if not url:
                continue
            ok = url in permalink_map
            st = "OK" if ok else "ROTO"
            checks.append({
                "kind": "internal_link",
                "label": field,
                "url": url,
                "status": st,
                "detail": "Destino encontrado." if ok else "No existe una ficha con ese permalink."
            })
            page_statuses.append(st)

        discovered = set(RELATIVE_URL_RE.findall(body))
        for raw in MARKDOWN_LINK_RE.findall(body):
            raw = raw.strip()
            if raw.startswith("http://") or raw.startswith("https://") or raw.startswith("#"):
                continue
            if "{{" in raw:
                continue
            discovered.add(raw)

        for raw in sorted(discovered):
            url = normalize_url(raw)
            if not url or url.startswith("/assets/"):
                continue
            ok = url in permalink_map
            st = "OK" if ok else "ROTO"
            checks.append({
                "kind": "internal_link",
                "label": "Enlace de contenido",
                "url": url,
                "status": st,
                "detail": "Destino encontrado." if ok else "No existe una ficha con ese permalink."
            })
            page_statuses.append(st)

        for media in data.get("media") or []:
            if not isinstance(media, dict):
                continue
            totals["recursos"] += 1
            mid = media.get("id") or "sin-id"
            storage = media.get("storage")
            provider = media.get("provider")
            derived = media.get("derived_from_version")
            mstatus = []
            detail = []

            if content_version is not None and derived is not None and derived != content_version:
                mstatus.append("REVISAR")
                detail.append(f"Derivado de versión {derived}; ficha en versión {content_version}.")
            elif content_version is not None and derived is None:
                mstatus.append("REVISAR")
                detail.append("Falta derived_from_version.")

            if storage == "internal":
                src = media.get("src")
                if not src:
                    mstatus.append("ROTO")
                    detail.append("src ausente.")
                else:
                    local = src.lstrip("/")
                    exists = (ROOT / local).exists()
                    mstatus.append("OK" if exists else "ROTO")
                    detail.append("Archivo interno encontrado." if exists else f"No existe {src}.")
            elif storage == "external":
                if provider == "youtube":
                    totals["videos_youtube"] += 1
                    ok, http_code, error = check_youtube(media.get("video_id"))
                    mstatus.append("OK" if ok else "ROTO")
                    detail.append(
                        f"YouTube responde ({http_code})." if ok
                        else f"YouTube no responde correctamente ({http_code or 'sin código'}): {error or 'error desconocido'}"
                    )
                else:
                    src = media.get("src")
                    if src and src.startswith(("http://", "https://")):
                        ok, http_code, error = check_http(src)
                        mstatus.append("OK" if ok else "ROTO")
                        detail.append(
                            f"Enlace externo responde ({http_code})." if ok
                            else f"Enlace externo no responde ({http_code or 'sin código'}): {error or 'error desconocido'}"
                        )
                    else:
                        mstatus.append("SIN COMPROBAR")
                        detail.append("Proveedor externo sin URL comprobable.")
            else:
                mstatus.append("SIN COMPROBAR")
                detail.append("storage no definido.")

            st = worst_status(mstatus)
            media_rows.append({
                "id": mid,
                "type": media.get("type"),
                "provider": provider,
                "storage": storage,
                "version": media.get("version"),
                "derived_from_version": derived,
                "status": st,
                "detail": " ".join(detail),
            })
            page_statuses.append(st)

        distribution = data.get("distribution") or {}
        youtube = distribution.get("youtube") if isinstance(distribution, dict) else None
        youtube_items = []
        if isinstance(youtube, dict):
            youtube_items = [youtube]
        elif isinstance(youtube, list):
            youtube_items = youtube

        for y in youtube_items:
            if not isinstance(y, dict):
                continue
            totals["videos_youtube"] += 1
            derived = y.get("derived_from_version")
            ystatuses = []
            detail = []
            if content_version is not None and derived is not None and derived != content_version:
                ystatuses.append("REVISAR")
                detail.append(f"Derivado de versión {derived}; ficha en versión {content_version}.")
            elif content_version is not None and derived is None:
                ystatuses.append("REVISAR")
                detail.append("Falta derived_from_version.")
            ok, http_code, error = check_youtube(y.get("video_id"))
            ystatuses.append("OK" if ok else "ROTO")
            detail.append(
                f"YouTube responde ({http_code})." if ok
                else f"YouTube no responde correctamente ({http_code or 'sin código'}): {error or 'error desconocido'}"
            )
            st = worst_status(ystatuses)
            media_rows.append({
                "id": y.get("id") or y.get("video_id") or "youtube",
                "type": "video",
                "provider": "youtube",
                "storage": "external",
                "version": y.get("version"),
                "derived_from_version": derived,
                "status": st,
                "detail": " ".join(detail),
            })
            page_statuses.append(st)

        overall = worst_status(page_statuses)
        key = {
            "OK": "ok",
            "REVISAR": "revisar",
            "ROTO": "rotos",
            "SIN COMPROBAR": "sin_comprobar",
        }[overall]
        totals[key] += 1

        items.append({
            "code": code,
            "title": title,
            "canonical_url": canonical,
            "content_version": content_version,
            "reviewed": data.get("reviewed"),
            "status": overall,
            "checks": checks,
            "media": media_rows,
        })

    items.sort(key=lambda x: (status_rank(x["status"]) * -1, x["code"]))
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": totals,
        "items": items,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(totals, ensure_ascii=False))

if __name__ == "__main__":
    main()
