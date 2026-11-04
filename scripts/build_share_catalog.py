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



def apply_approved_assembly(catalog, errors):
    """Une el calendario aprobado con las fichas, sin inventar activos multimedia.

    Las relaciones editoriales (principal/complementaria) no son publicaciones,
    ni equivalen a marketing_pieces con asset_ids comprobados.
    """
    for entry in catalog:
        entry["editorial_pieces"] = []
    path = ROOT / "_data" / "fr_ensamblaje_marketing.json"
    if not path.is_file():
        return None  # Los tests de catálogo y otras categorías no requieren FR.

    try:
        source = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        errors.append(f"{path}: no puede leerse el ensamblaje: {exc}")
        return None
    if (source.get("schema_version") != 1
            or source.get("category_code") != "FR"
            or source.get("approval") != "ensamblaje correcto - aprobado"):
        errors.append(f"{path}: falta la aprobación o el esquema esperado")
        return None
    pieces = source.get("pieces")
    if not isinstance(pieces, list):
        errors.append(f"{path}: pieces debe ser una lista")
        return None

    by_code = {item["code"]: item for item in catalog}
    roles = {"PRO": "promotores", "INV": "inversores", "COL": "colaboradores"}
    seen_pieces = set()
    linked_fichas = set()
    main_count = 0
    extra_count = 0
    for piece in pieces:
        if not isinstance(piece, dict):
            errors.append(f"{path}: pieza sin estructura")
            continue
        code, title, role = piece.get("code"), piece.get("title"), piece.get("role")
        if not isinstance(code, str) or not isinstance(title, str) or not title.strip():
            errors.append(f"{path}: pieza sin código/título válido")
            continue
        if code in seen_pieces:
            errors.append(f"{path}: pieza duplicada: {code}")
            continue
        seen_pieces.add(code)
        expected_role = roles.get(code.split("-", 1)[0])
        if (not expected_role or role != expected_role.capitalize()
                or not re.fullmatch(r"(PRO|INV|COL)-(EDU|INS|ENT|VEN)-\d{2}", code)):
            errors.append(f"{path}: código o rol de pieza inválidos: {code}")
            continue
        used_fichas = set()
        for key, label in (("principal", "Principal"), ("complementaria", "Complementaria")):
            ids = piece.get(key)
            if not isinstance(ids, list):
                errors.append(f"{path}: {code} debe declarar {key} como lista")
                continue
            for ficha_code in ids:
                if not isinstance(ficha_code, str) or ficha_code in used_fichas:
                    errors.append(f"{path}: referencia duplicada/inválida en {code}")
                    continue
                used_fichas.add(ficha_code)
                ficha = by_code.get(ficha_code)
                if not ficha:
                    errors.append(f"{path}: {code} remite a ficha inexistente {ficha_code}")
                    continue
                if (str(ficha.get("role") or "").casefold() != expected_role
                        or ficha.get("category") != source.get("category")):
                    errors.append(f"{path}: {code} y {ficha_code} pertenecen a roles/categorías diferentes")
                    continue
                ficha["editorial_pieces"].append({
                    "code": code,
                    "category_code": "FR",
                    "title": title,
                    "relation": label,
                    "assembly_status": "approved",
                })
                linked_fichas.add(ficha_code)
                if key == "principal":
                    main_count += 1
                else:
                    extra_count += 1

    relations = main_count + extra_count
    if len(seen_pieces) != source.get("expected_pieces"):
        errors.append(f"{path}: conteo de piezas distinto al aprobado")
    if relations != source.get("expected_relations"):
        errors.append(f"{path}: conteo de correspondencias distinto al aprobado")
    return {
        "source": source.get("source"),
        "approved_on": source.get("approved_on"),
        "pieces": len(seen_pieces),
        "relations": relations,
        "principal": main_count,
        "complementaria": extra_count,
        "linked_fichas": len(linked_fichas),
        "unlinked_fichas": sum(
            1 for entry in catalog
            if entry.get("category") == source.get("category")
            and entry["code"] not in linked_fichas
        ),
    }



def attach_verified_tiktok(catalog, errors):
    """Asocia publicaciones reales de TikTok con el ensamblaje editorial aprobado.

    Ficha principal: reproductor embebido con un ancla real generada por el
    include fr-tiktok-videos.html. Ficha complementaria: publicación externa.
    Ninguna asociación se deduce por semejanza de números ni del título.
    """
    path = ROOT / "_data" / "fr_tiktok_publicaciones.json"
    if not path.is_file():
        return None  # Mantiene compatibles las pruebas unitarias aisladas.

    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        errors.append(f"{path}: inventario TikTok ilegible: {exc}")
        return None
    if (registry.get("schema_version") != 1 or registry.get("platform") != "tiktok"
            or registry.get("account") != "@iskay.app"
            or not isinstance(registry.get("videos"), list)):
        errors.append(f"{path}: esquema TikTok inválido")
        return None

    videos = registry["videos"]
    by_code = {item["code"]: item for item in catalog}
    piece_index = {}
    for item in catalog:
        for piece in item.get("editorial_pieces", []):
            piece_index.setdefault(piece["code"], []).append((item, piece))

    seen_video_ids = set()
    seen_piece_codes = set()
    linked_pages = set()
    primary = related = 0
    for video in videos:
        if not isinstance(video, dict):
            errors.append(f"{path}: vídeo sin estructura")
            continue
        video_id, piece_code = str(video.get("video_id") or ""), video.get("piece_code")
        url, embed = video.get("share_url"), video.get("embed_link")
        if (not re.fullmatch(r"\d{12,25}", video_id)
                or not isinstance(piece_code, str)
                or video_id in seen_video_ids or piece_code in seen_piece_codes):
            errors.append(f"{path}: vídeo o pieza duplicados/inválidos: {piece_code}/{video_id}")
            continue
        seen_video_ids.add(video_id)
        seen_piece_codes.add(piece_code)

        # Solo usar URLs devueltas por la API de la cuenta oficial, sin
        # componer enlaces o asociar IDs del calendario por proximidad.
        try:
            share_parts, embed_parts = urlsplit(url), urlsplit(embed)
            expected_share = f"/@iskay.app/video/{video_id}"
            expected_embed = f"/player/v1/{video_id}"
            approved_url = (
                share_parts.scheme == embed_parts.scheme == "https"
                and share_parts.netloc == embed_parts.netloc == "www.tiktok.com"
                and share_parts.path == expected_share
                and embed_parts.path == expected_embed
                and not share_parts.username and not embed_parts.username
            )
        except (TypeError, ValueError):
            approved_url = False
        if not approved_url:
            errors.append(f"{path}: URL de publicación no verificable: {piece_code}")
            continue

        associations = piece_index.get(piece_code, [])
        if not associations:
            errors.append(f"{path}: {piece_code} no consta en el ensamblaje aprobado")
            continue
        for item, association in associations:
            relation = association["relation"]
            ficha_code = item["code"]
            asset_id = f"{ficha_code.lower()}-tiktok-{piece_code.lower()}"
            canonical = item["canonical_url"]
            asset = {
                "id": asset_id, "type": "video", "title": association["title"],
                "provider": "tiktok", "video_id": video_id,
                "derived_from_version": None,  # No inventar revisión funcional.
                "media_url": canonical + "#media-" + asset_id if relation == "Principal" else None,
                "original_url": url, "original_available": True,
            }
            # Evitar duplicar una referencia TikTok ya existente en el front matter;
            # FR-PRO-01 contenía un video_id sin URL original.
            matched_originals = [
                old for old in item["distribution"]
                if old.get("provider") == "tiktok" and old.get("video_id") == video_id
            ]
            for old in matched_originals:
                item["distribution"].remove(old)
                if old in item["unassigned_assets"]:
                    item["unassigned_assets"].remove(old)

            target = "media" if relation == "Principal" else "distribution"
            if any(x["id"] == asset_id for x in item[target]):
                errors.append(f"{path}: asset_id duplicado en {ficha_code}: {asset_id}")
                continue
            item[target].append(asset)
            group = next((g for g in item["marketing_pieces"] if g["code"] == piece_code), None)
            if group is None:
                group = {
                    "code": piece_code,
                    "category_code": "FR",
                    "title": association["title"],
                    "assets": [],
                }
                item["marketing_pieces"].append(group)
            if all(existing["id"] != asset_id for existing in group["assets"]):
                group["assets"].append(asset)
            linked_pages.add(ficha_code)
            if relation == "Principal":
                primary += 1
            else:
                related += 1

    links = primary + related
    if len(seen_video_ids) != registry.get("expected_videos"):
        errors.append(f"{path}: total de vídeos diferente del inventario aprobado")
    if links != registry.get("expected_relations"):
        errors.append(f"{path}: total de relaciones TikTok diferente del cruce aprobado")
    return {
        "platform": registry.get("platform"),
        "account": registry.get("account"),
        "verified_at": registry.get("verified_at"),
        "videos": len(seen_video_ids),
        "linked_fichas": len(linked_pages),
        "links": links,
        "principal": primary,
        "complementaria": related,
    }


def build_catalog():
    config = yaml.safe_load((ROOT / "_config.yml").read_text(encoding="utf-8"))
    taxonomy_path = ROOT / "_data" / "categories.yml"
    taxonomy = yaml.safe_load(taxonomy_path.read_text(encoding="utf-8")) if taxonomy_path.exists() else []
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
        # Las fichas antiguas pueden omitir role. Resolverlo desde el registro
        # común evita ofrecer «promotores» y «Promotores» como roles distintos.
        navigation_role = next((role.get("name") for category in (taxonomy or [])
                                for role in category.get("roles", [])
                                if role.get("url") and permalink.startswith(role["url"])), None)
        entry = {
            "code": code,
            "title": data.get("title"),
            "category": data.get("category") or parts[0],
            "role": data.get("role") or navigation_role or (parts[1] if len(parts) > 1 else None),
            "stage": data.get("stage"),
            "content_version": data.get("content_version"),
            "canonical_url": canonical,
            # Solo las fichas publicables deben aparecer en la búsqueda de usuarios;
            # el mantenimiento mantiene el inventario completo.
            "public_searchable": (
                data.get("published") is not False
                and data.get("visibility") != "private"
                and data.get("status") not in ("draft", "review", "archived")
            ),
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
                "video_id": video_id or None,
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

    assembly_report = apply_approved_assembly(catalog, errors)
    tiktok_report = attach_verified_tiktok(catalog, errors)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_fichas": len(catalog),
        "total_media": sum(len(entry["media"]) for entry in catalog),
        "total_distribution": sum(len(entry["distribution"]) for entry in catalog),
        "total_marketing_pieces": sum(len(entry["marketing_pieces"]) for entry in catalog),
        "total_unassigned_assets": sum(len(entry["unassigned_assets"]) for entry in catalog),
        "editorial_assembly": assembly_report,
        "verified_tiktok": tiktok_report,
        "total_editorial_pieces": assembly_report["pieces"] if assembly_report else 0,
        "total_editorial_links": assembly_report["relations"] if assembly_report else 0,
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
