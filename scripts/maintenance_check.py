#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import yaml

ROOT = Path(__file__).resolve().parents[1]
IDEAS = ROOT / "ideas"
OUT_DIR = ROOT / "mantenimiento"
OUT_FILE = OUT_DIR / "status.json"
TIKTOK_NEXT_REFRESH_FILE = OUT_DIR / "tiktok_refresh_token.next"
BASEURL = "/como-funciona"

RELATIVE_URL_RE = re.compile(r"""\{\{\s*['"]([^'"]+)['"]\s*\|\s*relative_url\s*\}\}""")
MARKDOWN_LINK_RE = re.compile(r"""\[[^\]]*\]\(([^)]+)\)""")

TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
TIKTOK_LIST_URL = "https://open.tiktokapis.com/v2/video/list/?fields=id,title,embed_link,share_url,create_time"
TIKTOK_QUERY_URL = "https://open.tiktokapis.com/v2/video/query/?fields=id,title,embed_link,share_url"

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

def request_json(url, *, method="GET", headers=None, data=None, timeout=15):
    req = Request(url, headers=headers or {}, data=data, method=method)
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8")), getattr(r, "status", 200)

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

def refresh_tiktok_access():
    client_key = os.getenv("TIKTOK_CLIENT_KEY", "").strip()
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET", "").strip()
    refresh_token = os.getenv("TIKTOK_REFRESH_TOKEN", "").strip()

    service = {
        "status": "SIN COMPROBAR",
        "detail": "Credenciales TikTok no configuradas.",
        "rotation_required": False,
        "recent_videos_checked": 0,
    }

    if not client_key or not client_secret or not refresh_token:
        return None, service

    payload = urlencode({
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }).encode("utf-8")

    try:
        data, code = request_json(
            TIKTOK_TOKEN_URL,
            method="POST",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Cache-Control": "no-cache",
                "User-Agent": "iskay-como-funciona-maintenance/1.0",
            },
            data=payload,
        )
    except HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            pass
        service.update(status="ROTO", detail=f"No se pudo renovar TikTok ({e.code}). {body[:220]}")
        return None, service
    except (URLError, TimeoutError, OSError) as e:
        service.update(status="SIN COMPROBAR", detail=f"No se pudo conectar con TikTok: {e}")
        return None, service

    access_token = data.get("access_token")
    new_refresh = data.get("refresh_token")
    if not access_token:
        service.update(status="ROTO", detail="TikTok no devolvió access_token al renovar.")
        return None, service

    if new_refresh and new_refresh != refresh_token:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        TIKTOK_NEXT_REFRESH_FILE.write_text(new_refresh, encoding="utf-8")
        service["rotation_required"] = True

    service.update(
        status="OK",
        detail="Autorización TikTok renovada correctamente.",
        expires_in=data.get("expires_in"),
        refresh_expires_in=data.get("refresh_expires_in"),
        scope=data.get("scope"),
    )
    return access_token, service

def list_tiktok_all(access_token, max_pages=100):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "User-Agent": "iskay-como-funciona-maintenance/1.0",
    }
    videos = []
    cursor = None

    for _ in range(max_pages):
        body = {"max_count": 20}
        if cursor is not None:
            body["cursor"] = cursor

        try:
            data, _ = request_json(
                TIKTOK_LIST_URL,
                method="POST",
                headers=headers,
                data=json.dumps(body).encode("utf-8"),
            )
        except Exception as e:
            return videos, str(e)

        error = data.get("error") or {}
        if error.get("code") not in (None, "", "ok", 0):
            return videos, f"{error.get('code')}: {error.get('message', '')}"

        page = data.get("data") or {}
        videos.extend(page.get("videos") or [])

        if not page.get("has_more"):
            return videos, None

        next_cursor = page.get("cursor")
        if next_cursor is None or next_cursor == cursor:
            return videos, "TikTok indicó más páginas pero no devolvió un cursor nuevo."
        cursor = next_cursor

    return videos, f"Se alcanzó el límite de seguridad de {max_pages} páginas."

def query_tiktok_videos(access_token, video_ids):
    result = {}
    if not access_token or not video_ids:
        return result, None

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "User-Agent": "iskay-como-funciona-maintenance/1.0",
    }

    ids = list(dict.fromkeys(str(v) for v in video_ids if v))
    for i in range(0, len(ids), 20):
        batch = ids[i:i+20]
        try:
            data, _ = request_json(
                TIKTOK_QUERY_URL,
                method="POST",
                headers=headers,
                data=json.dumps({"filters": {"video_ids": batch}}).encode("utf-8"),
            )
        except Exception as e:
            return result, str(e)

        error = data.get("error") or {}
        if error.get("code") not in (None, "", "ok", 0):
            return result, f"{error.get('code')}: {error.get('message', '')}"

        for video in (data.get("data") or {}).get("videos") or []:
            if video.get("id"):
                result[str(video["id"])] = video

    return result, None

def status_rank(status):
    return {"ROTO": 4, "REVISAR": 3, "SIN COMPROBAR": 2, "OK": 1}.get(status, 0)

def worst_status(statuses):
    statuses = [s for s in statuses if s]
    return max(statuses, key=status_rank) if statuses else "OK"

def normalize_distribution_items(value):
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    return []

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if TIKTOK_NEXT_REFRESH_FILE.exists():
        TIKTOK_NEXT_REFRESH_FILE.unlink()

    pages = []
    permalink_map = {}
    tiktok_ids = []
    tiktok_links = {}

    for path in sorted(IDEAS.rglob("*.md")):
        data, body = read_front_matter(path)
        if not data:
            continue
        rel = path.relative_to(ROOT).as_posix()
        permalink = normalize_url(data.get("permalink"))
        rec = {"path": rel, "data": data, "body": body}
        pages.append(rec)
        if permalink:
            permalink_map[permalink] = rec

        for media in data.get("media") or []:
            if isinstance(media, dict) and media.get("provider") == "tiktok" and media.get("video_id"):
                vid = str(media["video_id"])
                tiktok_ids.append(vid)
                tiktok_links.setdefault(vid, []).append({
                    "code": data.get("code"),
                    "title": data.get("title"),
                    "canonical_url": permalink,
                    "relation": "media",
                    "asset_id": media.get("id"),
                    "derived_from_version": media.get("derived_from_version"),
                })

        distribution = data.get("distribution") or {}
        if isinstance(distribution, dict):
            for item in normalize_distribution_items(distribution.get("tiktok")):
                if item.get("video_id"):
                    vid = str(item["video_id"])
                    tiktok_ids.append(vid)
                    tiktok_links.setdefault(vid, []).append({
                        "code": data.get("code"),
                        "title": data.get("title"),
                        "canonical_url": permalink,
                        "relation": "distribution",
                        "asset_id": item.get("id"),
                        "derived_from_version": item.get("derived_from_version"),
                    })

    access_token, tiktok_service = refresh_tiktok_access()
    all_tiktok = []
    tiktok_query = {}
    tiktok_query_error = None

    if access_token:
        all_tiktok, list_error = list_tiktok_all(access_token)
        if list_error:
            tiktok_service.update(status="ROTO", detail=f"Token válido, pero video.list falló: {list_error}")
        else:
            tiktok_service["recent_videos_checked"] = len(all_tiktok)
            tiktok_service["detail"] = f"TikTok conectado. Se pudieron leer {len(all_tiktok)} videos públicos."

        tiktok_query, tiktok_query_error = query_tiktok_videos(access_token, tiktok_ids)
        if tiktok_query_error and tiktok_ids:
            tiktok_service.update(status="ROTO", detail=f"video.query falló: {tiktok_query_error}")

    items = []
    totals = {
        "fichas": 0,
        "recursos": 0,
        "videos_youtube": 0,
        "videos_tiktok": 0,
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
                elif provider == "tiktok":
                    totals["videos_tiktok"] += 1
                    vid = str(media.get("video_id") or "")
                    if not vid:
                        mstatus.append("ROTO")
                        detail.append("video_id TikTok ausente.")
                    elif not access_token:
                        mstatus.append(tiktok_service["status"])
                        detail.append(tiktok_service["detail"])
                    elif tiktok_query_error:
                        mstatus.append("SIN COMPROBAR")
                        detail.append(f"No se pudo consultar TikTok: {tiktok_query_error}")
                    elif vid in tiktok_query:
                        mstatus.append("OK")
                        detail.append("Video TikTok encontrado para la cuenta autorizada.")
                    else:
                        mstatus.append("ROTO")
                        detail.append("TikTok no devolvió este video_id para la cuenta autorizada.")
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
        if isinstance(distribution, dict):
            youtube_items = normalize_distribution_items(distribution.get("youtube"))
            tiktok_items = normalize_distribution_items(distribution.get("tiktok"))
        else:
            youtube_items = []
            tiktok_items = []

        for y in youtube_items:
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

        for t in tiktok_items:
            totals["videos_tiktok"] += 1
            derived = t.get("derived_from_version")
            tstatuses = []
            detail = []
            if content_version is not None and derived is not None and derived != content_version:
                tstatuses.append("REVISAR")
                detail.append(f"Derivado de versión {derived}; ficha en versión {content_version}.")
            elif content_version is not None and derived is None:
                tstatuses.append("REVISAR")
                detail.append("Falta derived_from_version.")

            vid = str(t.get("video_id") or "")
            if not vid:
                tstatuses.append("ROTO")
                detail.append("video_id TikTok ausente.")
            elif not access_token:
                tstatuses.append(tiktok_service["status"])
                detail.append(tiktok_service["detail"])
            elif tiktok_query_error:
                tstatuses.append("SIN COMPROBAR")
                detail.append(f"No se pudo consultar TikTok: {tiktok_query_error}")
            elif vid in tiktok_query:
                tstatuses.append("OK")
                detail.append("Video TikTok encontrado para la cuenta autorizada.")
            else:
                tstatuses.append("ROTO")
                detail.append("TikTok no devolvió este video_id para la cuenta autorizada.")

            st = worst_status(tstatuses)
            media_rows.append({
                "id": t.get("id") or vid or "tiktok",
                "type": "video",
                "provider": "tiktok",
                "storage": "external",
                "version": t.get("version"),
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

    tiktok_inventory_videos = []
    for video in all_tiktok:
        vid = str(video.get("id") or "")
        links = tiktok_links.get(vid, [])
        tiktok_inventory_videos.append({
            "video_id": vid,
            "title": video.get("title") or "",
            "create_time": video.get("create_time"),
            "embed_link": video.get("embed_link"),
            "share_url": video.get("share_url"),
            "status": "VINCULADO" if links else "SIN VINCULAR",
            "links": links,
        })

    tiktok_inventory = {
        "total": len(tiktok_inventory_videos),
        "linked": sum(1 for x in tiktok_inventory_videos if x["status"] == "VINCULADO"),
        "unlinked": sum(1 for x in tiktok_inventory_videos if x["status"] == "SIN VINCULAR"),
        "videos": tiktok_inventory_videos,
    }

    items.sort(key=lambda x: (status_rank(x["status"]) * -1, x["code"]))
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": totals,
        "services": {"tiktok": tiktok_service},
        "tiktok_inventory": tiktok_inventory,
        "items": items,
    }

    OUT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"summary": totals, "tiktok": tiktok_service}, ensure_ascii=False))

if __name__ == "__main__":
    main()
