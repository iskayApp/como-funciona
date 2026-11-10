"""Recompensa TikTok: dos publicaciones reales para Promotores, otros roles vacíos.

Las pruebas comprueban la atribución por categoría y no autorizan revisiones
editoriales. Nunca se deducen vídeos de códigos de producción coincidentes.
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import build_share_catalog as catalog
from scripts.video_publications import load_explicit_tiktok

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "_data/recompensa_tiktok_publicaciones.json").read_text(encoding="utf-8"))


def catalog_items():
    return [
        {
            "code": code, "category": category, "role": role,
            "title": code, "canonical_url": "https://example.test/" + code.lower() + "/",
            "content_version": 1, "editorial_status": "pending_review",
            "reviewed": False, "media": [], "distribution": [],
            "marketing_pieces": [], "unassigned_assets": [], "editorial_pieces": [],
        }
        for code, category, role in [
            ("CF-REC-PRO-001", "Recompensa", "Promotores"),
            ("CF-REC-PRO-004", "Recompensa", "Promotores"),
            ("CF-REC-CON-001", "Recompensa", "Contribuyentes"),
            ("CF-REC-COL-001", "Recompensa", "Colaboradores"),
            ("CF-DON-PRO-009", "Donación", "Promotores"),
        ]
    ]


class RecompensaTikTokTests(unittest.TestCase):
    def test_real_tiktok_inventory_two_posts_only_for_promotores(self):
        self.assertEqual(REGISTRY["category_code"], "REC")
        self.assertEqual(REGISTRY["category"], "Recompensa")
        self.assertEqual(REGISTRY["account"], "@iskay.app")
        self.assertTrue(REGISTRY["inventory_complete"])
        self.assertEqual(REGISTRY["association_status"], "pending_review")
        self.assertEqual(REGISTRY["expected_videos"], 2)
        self.assertEqual(REGISTRY["expected_relations"], 2)
        self.assertEqual(REGISTRY["audience_summary"], {
            "Promotores": 2, "Contribuyentes": 0, "Colaboradores": 0,
        })
        self.assertEqual({x["video_id"] for x in REGISTRY["videos"]}, {
            "7678066820368059670", "7678427855948221718",
        })
        self.assertEqual({x["piece_code"] for x in REGISTRY["videos"]}, {
            "PRO-ENT-01", "PRO-ENT-02",
        })
        self.assertEqual({x["complementaria"][0] for x in REGISTRY["videos"]}, {
            "CF-REC-PRO-001", "CF-REC-PRO-004",
        })
        self.assertTrue(all(x["principal"] == [] for x in REGISTRY["videos"]))
        for item in REGISTRY["videos"]:
            self.assertIn(f'/@iskay.app/video/{item["video_id"]}', item["share_url"])
            self.assertIn(f'/player/v1/{item["video_id"]}', item["embed_link"])
            self.assertIn("Producción", item["evidence"]["production_document"])
            self.assertIn("scope_limit", item["evidence"])

    def test_explicit_mapping_and_marketing_control_without_editorial_approval(self):
        rows = catalog_items()
        registry, links = load_explicit_tiktok(
            ROOT, {r["code"]: r for r in rows}, [], category_code="REC")
        self.assertIsNotNone(registry)
        self.assertEqual(len(links), 2)
        self.assertEqual({link["ficha_code"] for link in links}, {
            "CF-REC-PRO-001", "CF-REC-PRO-004",
        })
        errors = []
        attached = catalog.attach_explicit_tiktok(rows, errors, category_code="REC")
        self.assertEqual(errors, [])
        self.assertEqual(attached["links"], 2)
        self.assertEqual(attached["videos"], 2)
        self.assertEqual(attached["principal"], 0)
        self.assertEqual(attached["complementaria"], 2)
        self.assertEqual(attached["linked_fichas"], 2)
        for row in rows:
            self.assertEqual(row["editorial_status"], "pending_review")
            self.assertIs(row["reviewed"], False)
            if row["code"].startswith("CF-REC-PRO-"):
                self.assertEqual(len(row["media"]), 1)
                self.assertEqual(len(row["marketing_pieces"]), 1)
                media = row["media"][0]
                self.assertEqual(media["category_code"], "REC")
                self.assertEqual(media["editorial_relation"], "Complementaria")
                self.assertEqual(media["association_status"], "pending_review")
                self.assertIsNone(media["derived_from_version"])
                self.assertEqual(media["media_url"], row["canonical_url"] + "#media-" + media["id"])
            else:
                self.assertEqual(row["media"], [])
                self.assertEqual(row["marketing_pieces"], [])
        self.assertEqual(catalog.combined_tiktok_report(
            {"videos": 6, "links": 16, "linked_fichas": 9, "principal": 8, "complementaria": 8},
            {"videos": 3, "links": 6, "linked_fichas": 4, "principal": 3, "complementaria": 3},
            attached)["videos"], 11)

    def test_invalid_or_cross_role_association_never_renders(self):
        rows = catalog_items()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "_data").mkdir()
            def validate(data):
                (root / "_data/recompensa_tiktok_publicaciones.json").write_text(
                    json.dumps(data, ensure_ascii=False), encoding="utf-8")
                errors = []
                result = load_explicit_tiktok(root, {r["code"]: r for r in rows},
                                              errors, category_code="REC")
                return result, errors
            for bad_code in ("CF-REC-CON-001", "CF-REC-COL-001", "CF-DON-PRO-009"):
                with self.subTest(bad_code=bad_code):
                    data = copy.deepcopy(REGISTRY)
                    data["videos"][0]["complementaria"] = [bad_code]
                    result, errors = validate(data)
                    self.assertEqual(result, (None, []))
                    self.assertTrue(errors)
            data = copy.deepcopy(REGISTRY)
            data["videos"][0]["share_url"] = "https://www.tiktok.com/@other/video/7678066820368059670"
            self.assertEqual(validate(data)[0], (None, []))
            data = copy.deepcopy(REGISTRY)
            data["videos"][0]["video_id"] = data["videos"][1]["video_id"]
            self.assertEqual(validate(data)[0], (None, []))
            data = copy.deepcopy(REGISTRY)
            data["audience_summary"]["Contribuyentes"] = 1
            self.assertEqual(validate(data)[0], (None, []))


if __name__ == "__main__":
    unittest.main()
