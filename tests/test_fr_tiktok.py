"""TikTok publicado: asociación por código de pieza y ficha, sin inventar URLs."""
import copy
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from scripts import build_share_catalog as catalog

ROOT = Path(__file__).resolve().parents[1]


class TikTokApprovedAssemblyTests(unittest.TestCase):
    def setUp(self):
        self.assembly = json.loads((ROOT / "_data/fr_ensamblaje_marketing.json").read_text(encoding="utf-8"))
        self.registry = json.loads((ROOT / "_data/fr_tiktok_publicaciones.json").read_text(encoding="utf-8"))
        self.pieces = {p["code"]: p for p in self.assembly["pieces"]}
        self.refs = {}
        for video in self.registry["videos"]:
            piece = self.pieces[video["piece_code"]]
            for relation in ("principal", "complementaria"):
                for code in piece[relation]:
                    self.refs.setdefault(code, []).append({
                        "code": video["piece_code"],
                        "category_code": "FR",
                        "title": piece["title"],
                        "relation": relation.capitalize(),
                        "assembly_status": "approved",
                    })

    def fake_catalog(self):
        items = []
        for code, associations in self.refs.items():
            items.append({
                "code": code, "category": "Financiamiento Reembolsable",
                "role": "promotores",
                "title": code,
                "canonical_url": "https://iskayapp.github.io/como-funciona/fr/" + code.lower() + "/",
                "editorial_pieces": associations,
                "media": [], "distribution": [],
                "marketing_pieces": [], "unassigned_assets": [],
            })
        return items

    def test_exact_production_codes_and_official_publications(self):
        self.assertEqual(self.registry["schema_version"], 1)
        self.assertEqual(self.registry["platform"], "tiktok")
        self.assertEqual(self.registry["account"], "@iskay.app")
        self.assertEqual(len(self.registry["videos"]), 6)
        self.assertEqual(self.registry["expected_relations"], 16)
        self.assertEqual(len(self.refs), 9)
        seen_ids, seen_pieces = set(), set()
        for row in self.registry["videos"]:
            piece = row["piece_code"]
            self.assertIn(piece, self.pieces)
            self.assertEqual(self.pieces[piece]["role"], "Promotores")
            self.assertNotIn(row["video_id"], seen_ids)
            self.assertNotIn(piece, seen_pieces)
            seen_ids.add(row["video_id"])
            seen_pieces.add(piece)
            self.assertIn("/@iskay.app/video/" + row["video_id"], row["share_url"])
            self.assertIn("/player/v1/" + row["video_id"], row["embed_link"])
        self.assertEqual(seen_pieces, {
            "PRO-EDU-01", "PRO-INS-01", "PRO-EDU-06",
            "PRO-INS-02", "PRO-EDU-07", "PRO-EDU-17",
        })

    def test_all_six_videos_have_correct_main_and_secondary_links(self):
        entries = self.fake_catalog()
        errors = []
        status = catalog.attach_verified_tiktok(entries, errors)
        self.assertEqual(errors, [])
        self.assertEqual(status["videos"], 6)
        self.assertEqual(status["links"], 16)
        self.assertEqual(status["principal"], 8)
        self.assertEqual(status["complementaria"], 8)
        self.assertEqual(status["linked_fichas"], 9)
        for entry in entries:
            self.assertEqual(len(entry["marketing_pieces"]), len(entry["editorial_pieces"]))
            self.assertEqual(len(entry["media"]) + len(entry["distribution"]), len(entry["editorial_pieces"]))
            for group in entry["marketing_pieces"]:
                self.assertEqual(len(group["assets"]), 1)
                asset = group["assets"][0]
                self.assertEqual(asset["provider"], "tiktok")
                self.assertTrue(asset["original_available"])
                self.assertIn("/@iskay.app/video/", asset["original_url"])
                self.assertIsNone(asset["derived_from_version"])
                relation = next(p["relation"] for p in entry["editorial_pieces"] if p["code"] == group["code"])
                self.assertEqual(asset['editorial_relation'], relation)
                self.assertEqual(asset["media_url"], entry["canonical_url"] + "#media-" + asset["id"])
                self.assertIn(asset, entry["media"])
                self.assertNotIn(asset, entry["distribution"])

    def test_old_reference_is_promoted_and_not_duplicated(self):
        entries = self.fake_catalog()
        entry = next(e for e in entries if e["code"] == "FR-PRO-01")
        old = {"id": "fr-pro-01-tiktok-01",
               "provider": "tiktok", "video_id": "7701409317936844054",
               "original_url": None, "original_available": False,
               "derived_from_version": 1}
        entry["distribution"].append(old)
        entry["unassigned_assets"].append(old)
        errors = []
        result = catalog.attach_verified_tiktok(entries, errors)
        self.assertEqual(errors, [])
        self.assertEqual(result["videos"], 6)
        self.assertNotIn(old, entry["distribution"])
        self.assertNotIn(old, entry["unassigned_assets"])
        self.assertEqual(sum(x.get("video_id") == old["video_id"]
                             for x in entry["media"] + entry["distribution"]), 1)
        for item in entries:
            for asset in item["media"] + item["distribution"]:
                exact_match = item["code"] == entry["code"] and asset.get("video_id") == old["video_id"]
                self.assertEqual(asset["derived_from_version"], 1 if exact_match else None)

    def test_unrelated_ficha_does_not_inherit_any_video(self):
        entries = self.fake_catalog()
        unrelated = copy.deepcopy(entries[0])
        unrelated.update(code='CF-FR-INV-001', editorial_pieces=[], media=[], distribution=[], marketing_pieces=[], unassigned_assets=[])
        entries.append(unrelated)
        errors = []
        catalog.attach_verified_tiktok(entries, errors)
        self.assertEqual(errors, [])
        self.assertEqual(unrelated['media'], [])
        self.assertEqual(unrelated['distribution'], [])
        self.assertEqual(unrelated['marketing_pieces'], [])

    def test_bad_url_or_duplicate_publication_must_fail(self):
        def validate(data):
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                (root / "_data").mkdir()
                (root / "_data/fr_tiktok_publicaciones.json").write_text(
                    json.dumps(data, ensure_ascii=False), encoding="utf-8"
                )
                errors = []
                with patch.object(catalog, "ROOT", root):
                    catalog.attach_verified_tiktok(self.fake_catalog(), errors)
                return errors

        bad_url = copy.deepcopy(self.registry)
        bad_url["videos"][0]["share_url"] = "https://ejemplo.invalid/video/123"
        self.assertTrue(any("URL de publicación no verificable" in e for e in validate(bad_url)))

        duplicate = copy.deepcopy(self.registry)
        duplicate["videos"].append(copy.deepcopy(duplicate["videos"][0]))
        self.assertTrue(any("duplicados/inválidos" in e for e in validate(duplicate)))

    def test_known_embedded_video_keeps_its_version_and_existing_piece_reference(self):
        entries = self.fake_catalog()
        entry = next(e for e in entries if e["code"] == "FR-PRO-01")
        video = next(row for row in self.registry["videos"] if row["piece_code"] == "PRO-EDU-01")
        old = {"id": "old-embedded-reference", "provider": "tiktok",
               "video_id": video["video_id"], "derived_from_version": 2}
        entry["media"].append(old)
        entry["marketing_pieces"].append({"code": "PRO-EDU-01", "assets": [old]})
        errors = []
        catalog.attach_verified_tiktok(entries, errors)
        self.assertEqual(errors, [])
        group = next(group for group in entry["marketing_pieces"] if group["code"] == "PRO-EDU-01")
        self.assertEqual(len(group["assets"]), 1)
        asset = group["assets"][0]
        self.assertEqual(asset["derived_from_version"], 2)
        self.assertIn(asset, entry["media"])
        self.assertNotIn(old, entry["media"])
        self.assertTrue(asset["original_available"])


if __name__ == "__main__":
    unittest.main()
