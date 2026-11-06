"""Explicit Donación videos remain separate from FR and from editorial approval."""
import copy
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from scripts import build_share_catalog as catalog
from scripts import maintenance_check as maintenance
from scripts.video_publications import load_explicit_tiktok


VIDEO_ID = "7674293282129595670"
FR_VIDEO_ID = "7687702006810545440"


def urls(video_id):
    return {
        "share_url": f"https://www.tiktok.com/@iskay.app/video/{video_id}?utm_source=test",
        "embed_link": f"https://www.tiktok.com/player/v1/{video_id}?autoplay=1&loop=1",
    }


def registry():
    return {
        "schema_version": 1, "platform": "tiktok", "account": "@iskay.app",
        "category_code": "DON", "category": "Donación", "association_status": "pending_review",
        "publication_authorized_on": "2026-11-06", "verified_at": "2026-11-06T13:15:39Z",
        "source": "Publicación verificada y documento de producción de prueba",
        "expected_videos": 1, "expected_relations": 2,
        "videos": [{
            "piece_code": "PRO-EDU-02", "video_id": VIDEO_ID, "title": "Presentar una iniciativa",
            "published_at": "2026-08-15T16:17:31Z", **urls(VIDEO_ID),
            "principal": ["CF-DON-PRO-009"], "complementaria": ["CF-DON-PRO-010"],
            "evidence": {"production_document": "PRO-EDU-02 - Producción"},
        }],
    }


def entries():
    rows = []
    for code, category in (("CF-DON-PRO-009", "Donación"), ("CF-DON-PRO-010", "Donación"),
                           ("FR-PRO-07", "Financiamiento Reembolsable")):
        rows.append({
            "code": code, "category": category, "role": "Promotores", "title": code,
            "content_version": 1, "editorial_status": "pending_review", "reviewed": False,
            "permalink": "/test/" + code.lower() + "/",
            "canonical_url": "https://example.test/como-funciona/test/" + code.lower() + "/",
            "media": [], "distribution": [], "marketing_pieces": [], "unassigned_assets": [],
            "editorial_pieces": [],
        })
    rows[-1]["editorial_pieces"] = [{
        "code": "PRO-EDU-02", "category_code": "FR", "title": "Condiciones del financiamiento",
        "relation": "Principal", "assembly_status": "approved",
    }]
    return rows


class DonationPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "_data").mkdir()

    def write(self, data):
        (self.root / "_data/donacion_tiktok_publicaciones.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def check(self, data, rows=None):
        self.write(data)
        errors = []
        result = load_explicit_tiktok(self.root, {r["code"]: r for r in rows or entries()}, errors)
        return result, errors

    def test_missing_registry_does_not_change_legacy_catalog(self):
        rows = entries()
        before = copy.deepcopy(rows)
        errors = []
        with patch.object(catalog, "ROOT", self.root):
            self.assertIsNone(catalog.attach_explicit_tiktok(rows, errors))
        self.assertEqual(rows, before)
        self.assertEqual(errors, [])

    def test_same_piece_code_is_scoped_by_category_and_never_approves_donation(self):
        self.write(registry())
        fr = {
            "schema_version": 1, "platform": "tiktok", "account": "@iskay.app",
            "verified_at": "2026-11-04T15:40:41Z", "expected_videos": 1, "expected_relations": 1,
            "videos": [{"piece_code": "PRO-EDU-02", "video_id": FR_VIDEO_ID, **urls(FR_VIDEO_ID)}],
        }
        (self.root / "_data/fr_tiktok_publicaciones.json").write_text(json.dumps(fr))
        rows, errors = entries(), []
        with patch.object(catalog, "ROOT", self.root):
            fr_result = catalog.attach_verified_tiktok(rows, errors)
            fr_before = copy.deepcopy(rows[-1])
            donation_result = catalog.attach_explicit_tiktok(rows, errors)
        self.assertEqual(errors, [])
        self.assertEqual(rows[-1], fr_before)
        self.assertEqual(fr_result["videos"], 1)
        self.assertEqual(donation_result["links"], 2)
        self.assertEqual(donation_result["association_status"], "pending_review")
        self.assertEqual(catalog.combined_tiktok_report(fr_result, donation_result)["videos"], 2)
        self.assertEqual(catalog.combined_tiktok_report(fr_result, None), fr_result)
        for item, relation in zip(rows[:2], ("Principal", "Complementaria")):
            self.assertEqual(item["editorial_status"], "pending_review")
            self.assertIs(item["reviewed"], False)
            self.assertEqual(item["editorial_pieces"], [])
            self.assertEqual(len(item["media"]), 1)
            asset = item["media"][0]
            self.assertEqual(asset["video_id"], VIDEO_ID)
            self.assertIsNone(asset["derived_from_version"])
            self.assertEqual(asset["association_status"], "pending_review")
            self.assertEqual(asset["editorial_relation"], relation)
            self.assertEqual(asset["media_url"], item["canonical_url"] + "#media-" + asset["id"])
            group = item["marketing_pieces"][0]
            self.assertEqual((group["category_code"], group["code"]), ("DON", "PRO-EDU-02"))
            self.assertEqual(group["association_status"], "pending_review")
            self.assertEqual(group["assets"], [asset])

    def test_wrong_account_id_host_or_category_rejects_the_whole_registry(self):
        changes = [
            ("share_url", f"https://www.tiktok.com/@otra.cuenta/video/{VIDEO_ID}"),
            ("share_url", f"https://www.tiktok.com.ejemplo.invalid/@iskay.app/video/{VIDEO_ID}"),
            ("embed_link", f"https://www.tiktok.com/player/v1/{FR_VIDEO_ID}"),
            ("share_url", urls(VIDEO_ID)["share_url"] + "#otro"),
        ]
        for key, value in changes:
            with self.subTest(key=key, value=value):
                data = registry()
                data["videos"][0][key] = value
                result, errors = self.check(data)
                self.assertEqual(result, (None, []))
                self.assertTrue(any("URL de publicación no verificable" in e for e in errors))
        for destination in ("FR-PRO-07", "CF-DON-PRO-999"):
            with self.subTest(destination=destination):
                data = registry()
                data["videos"][0]["principal"] = [destination]
                result, errors = self.check(data)
                self.assertEqual(result, (None, []))
                self.assertTrue(errors)

    def test_incomplete_provenance_duplicate_relation_or_wrong_metadata_fail(self):
        mutations = [
            lambda d: d.pop("publication_authorized_on"),
            lambda d: d.update(association_status="approved"),
            lambda d: d.update(category_code="FR"),
            lambda d: d["videos"][0].pop("evidence"),
            lambda d: d["videos"][0].pop("title"),
            lambda d: d["videos"][0].update(complementaria=["CF-DON-PRO-009"]),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(case=index):
                data = registry()
                mutate(data)
                result, errors = self.check(data)
                self.assertEqual(result, (None, []))
                self.assertTrue(errors)
        rows = entries()
        rows[0]["category"] = "Financiamiento Reembolsable"
        result, errors = self.check(registry(), rows)
        self.assertEqual(result, (None, []))
        self.assertTrue(any("categoría o rol" in e for e in errors))

    def diagnostic(self, *, missing=False, connected=True):
        self.write(registry())
        ideas = self.root / "ideas/donacion"
        ideas.mkdir(parents=True, exist_ok=True)
        for item in entries()[:2]:
            (ideas / (item["code"] + ".md")).write_text(
                "---\n" + yaml.safe_dump(item, allow_unicode=True) + "---\n# " + item["title"] + "\n")
        available = {} if missing else {VIDEO_ID: {"id": VIDEO_ID, "title": "Vídeo", **urls(VIDEO_ID)}}
        output = self.root / "status.json"
        service = {"status": "OK" if connected else "SIN COMPROBAR", "detail": "Servicio simulado"}
        with patch.object(maintenance, "ROOT", self.root), \
                patch.object(maintenance, "IDEAS", self.root / "ideas"), \
                patch.object(maintenance, "OUT_DIR", self.root), \
                patch.object(maintenance, "OUT_FILE", output), \
                patch.object(maintenance, "TIKTOK_NEXT_REFRESH_FILE", self.root / "token.next"), \
                patch.object(maintenance, "refresh_tiktok_access", return_value=("fixture" if connected else None, service)), \
                patch.object(maintenance, "list_tiktok_all", return_value=(list(available.values()), None)), \
                patch.object(maintenance, "query_tiktok_videos", return_value=(available, None)) as query, \
                patch.dict(maintenance.os.environ, {"GITHUB_SHA": "a" * 40}), \
                redirect_stdout(io.StringIO()):
            maintenance.main()
        if connected:
            self.assertEqual(set(query.call_args.args[1]), {VIDEO_ID})
        else:
            query.assert_not_called()
        return json.loads(output.read_text())

    def test_diagnostic_checks_both_relations_without_claiming_editorial_review(self):
        report = self.diagnostic()
        self.assertEqual(report["summary"]["videos_tiktok"], 1)
        self.assertEqual(report["summary"]["relaciones_tiktok"], 2)
        for item in report["items"]:
            self.assertEqual(len(item["media"]), 1)
            asset = item["media"][0]
            self.assertEqual(asset["status"], "REVISAR")
            self.assertEqual(asset["association_status"], "pending_review")
            self.assertEqual(asset["category_code"], "DON")
            self.assertIsNone(asset["derived_from_version"])
            self.assertIsNone(asset["reviewed"])
            self.assertIn("encontrado", asset["detail"])
            self.assertIn("pendiente de revisión", asset["detail"])
        links = report["tiktok_inventory"]["videos"][0]["links"]
        self.assertEqual({link["editorial_relation"] for link in links}, {"Principal", "Complementaria"})
        self.assertTrue(all(link["relation"] == "media" for link in links))

    def test_removed_video_marks_every_relation_broken(self):
        report = self.diagnostic(missing=True)
        self.assertEqual(len(report["items"]), 2)
        for item in report["items"]:
            self.assertEqual(item["status"], "ROTO")
            self.assertEqual(item["media"][0]["status"], "ROTO")
            self.assertIn("no devolvió", item["media"][0]["detail"])

    def test_unavailable_api_never_silently_passes_donation_relations(self):
        report = self.diagnostic(connected=False)
        self.assertFalse(report["tiktok_inventory"]["complete"])
        for item in report["items"]:
            self.assertNotEqual(item["media"][0]["status"], "OK")
            self.assertIn("Servicio simulado", item["media"][0]["detail"])


if __name__ == "__main__":
    unittest.main()
