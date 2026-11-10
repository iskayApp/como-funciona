"""Validate explicitly linked publications without granting editorial approval.

The Donación registry is independent of the approved FR assembly. A production
code only identifies a piece within its category; the registry names every ficha
that may receive its player. This module performs no network or write operation.
"""
from datetime import date, datetime
import json
from pathlib import Path
import re
from urllib.parse import urlsplit


ROLE_NAMES = {"PRO": "Promotores", "DON": "Donantes", "COL": "Colaboradores"}
CATEGORY_ROLES = {
    "DON": ROLE_NAMES,
    "REC": {"PRO": "Promotores", "CON": "Contribuyentes", "COL": "Colaboradores"},
}
CATEGORY_NAMES = {"DON": "Donación", "REC": "Recompensa"}



def official_tiktok_urls(video_id, share_url, embed_link):
    """Accept only the real account/player pair for the same publication ID."""
    try:
        share, embed = urlsplit(share_url), urlsplit(embed_link)
        return (
            share.scheme == embed.scheme == "https"
            and share.netloc == embed.netloc == "www.tiktok.com"
            and share.path == f"/@iskay.app/video/{video_id}"
            and embed.path == f"/player/v1/{video_id}"
            and not share.username and not embed.username
            and not share.fragment and not embed.fragment
        )
    except (TypeError, ValueError):
        return False


def iso_timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.tzinfo is not None
    except (AttributeError, TypeError, ValueError):
        return False


def load_explicit_tiktok(root, fichas, errors, category_code="DON"):
    """Validate Donación or Recompensa explicitly, never approve editorial content.

    Each category has an independent registry; production codes are scoped by
    category. Missing registries return no relations, and any malformed registry
    returns no relations so a partial publication cannot leak into the catalog.
    """
    if category_code not in CATEGORY_NAMES:
        errors.append(f"Categoría TikTok no admitida: {category_code}")
        return None, []
    category_name = CATEGORY_NAMES[category_code]
    role_names = CATEGORY_ROLES[category_code]
    accepted_roles = "|".join(role_names)
    filename = "donacion_tiktok_publicaciones.json" if category_code == "DON" else "recompensa_tiktok_publicaciones.json"
    path = Path(root) / "_data" / filename
    if not path.is_file():
        return None, []
    start_errors = len(errors)
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f"{path}: inventario de publicaciones ilegible: {exc}")
        return None, []
    if not isinstance(registry, dict) or (
            registry.get("schema_version") != 1
            or registry.get("platform") != "tiktok"
            or registry.get("account") != "@iskay.app"
            or registry.get("category_code") != category_code
            or registry.get("category") != category_name
            or registry.get("association_status") != "pending_review"
            or not isinstance(registry.get("videos"), list)):
        errors.append(f"{path}: esquema, categoría o estado de asociación inválidos")
        return None, []
    try:
        date.fromisoformat(registry.get("publication_authorized_on"))
    except (TypeError, ValueError):
        errors.append(f"{path}: falta la fecha de autorización de publicación")
    if not iso_timestamp(registry.get("verified_at")) or not registry.get("source"):
        errors.append(f"{path}: faltan la fecha o fuente de comprobación pública")
    if len(errors) != start_errors:
        return None, []

    associations, seen_ids, seen_pieces = [], set(), set()
    for video in registry["videos"]:
        if not isinstance(video, dict):
            errors.append(f"{path}: vídeo sin estructura")
            continue
        video_id = str(video.get("video_id") or "")
        piece_code = video.get("piece_code")
        piece_key = (registry["category_code"], piece_code)
        if (not re.fullmatch(r"\d{12,25}", video_id)
                or not isinstance(piece_code, str)
                or not re.fullmatch(rf"(?:{accepted_roles})-(?:EDU|INS|ENT|VEN)-\d{{2}}", piece_code)
                or video_id in seen_ids or piece_key in seen_pieces):
            errors.append(f"{path}: vídeo o pieza duplicados/inválidos: {piece_code}/{video_id}")
            continue
        seen_ids.add(video_id)
        seen_pieces.add(piece_key)
        video_errors = len(errors)
        if not official_tiktok_urls(video_id, video.get("share_url"), video.get("embed_link")):
            errors.append(f"{path}: URL de publicación no verificable: {piece_code}")
        if (not isinstance(video.get("title"), str) or not video["title"].strip()
                or not iso_timestamp(video.get("published_at")) or not video.get("evidence")):
            errors.append(f"{path}: {piece_code} necesita título, fecha y evidencia del cruce")
        if len(errors) != video_errors:
            continue
        seen_fichas = set()
        for key, label in (("principal", "Principal"), ("complementaria", "Complementaria")):
            codes = video.get(key)
            if not isinstance(codes, list):
                errors.append(f"{path}: {piece_code} debe declarar {key} como lista")
                continue
            for code in codes:
                match = re.fullmatch(rf"CF-{category_code}-({accepted_roles})-\d{{3}}", code) if isinstance(code, str) else None
                if not match or code in seen_fichas:
                    errors.append(f"{path}: referencia duplicada o de otra categoría en {piece_code}: {code}")
                    continue
                seen_fichas.add(code)
                if category_code == "REC" and piece_code.split("-")[0] != match[1]:
                    errors.append(f"{path}: vídeo {piece_code} no está dirigido al rol de {code}")
                    continue
                ficha = fichas.get(code)
                if not ficha:
                    errors.append(f"{path}: {piece_code} referencia ficha inexistente: {code}")
                    continue
                if (ficha.get("category") != registry["category"]
                        or str(ficha.get("role", "")).casefold() != role_names[match[1]].casefold()):
                    errors.append(f"{path}: categoría o rol de ficha incorrectos: {piece_code}/{code}")
                    continue
                associations.append({
                    "ficha_code": code, "piece_code": piece_code,
                    "category_code": registry["category_code"], "category": registry["category"],
                    "title": video["title"], "relation": label,
                    "video_id": video_id, "share_url": video.get("share_url"),
                    "embed_link": video.get("embed_link"), "published_at": video.get("published_at"),
                    "association_status": registry["association_status"],
                    "publication_authorized_on": registry["publication_authorized_on"],
                })
        if not seen_fichas:
            errors.append(f"{path}: {piece_code} no declara ninguna ficha relacionada")
    if category_code == "REC" and "audience_summary" in registry:
        actual_audience = {role: 0 for role in role_names.values()}
        for video in registry["videos"]:
            audience = role_names.get(str(video.get("piece_code") or "").split("-")[0])
            if audience:
                actual_audience[audience] += 1
        if actual_audience != registry["audience_summary"]:
            errors.append(f"{path}: número de vídeos por rol no corresponde al inventario")

    if len(seen_ids) != registry.get("expected_videos"):
        errors.append(f"{path}: total de vídeos diferente del registro")
    if len(associations) != registry.get("expected_relations"):
        errors.append(f"{path}: total de relaciones diferente del registro")
    if len(errors) != start_errors:
        return None, []
    return registry, associations
