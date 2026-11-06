"""El diagnóstico debe cubrir cada publicación del ensamblaje, sin llamadas de red."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import maintenance_check as maintenance


ROOT = Path(__file__).resolve().parents[1]


class MaintenanceTikTokRegistryTests(unittest.TestCase):
    def setUp(self):
        registry = json.loads((ROOT / "_data/fr_tiktok_publicaciones.json").read_text(encoding="utf-8"))
        self.expected_relations = registry["expected_relations"]
        self.videos = [{
            "id": row["video_id"], "title": row.get("title") or row["piece_code"],
            "share_url": row["share_url"], "embed_link": row["embed_link"],
        } for row in registry["videos"]]
        self.by_id = {row["id"]: row for row in self.videos}

    def report(self, missing=None, connected=True, list_error=None):
        available = {key: value for key, value in self.by_id.items() if key != missing}
        service = {"status": "OK" if connected else "SIN COMPROBAR",
                   "detail": "Servicio simulado para esta prueba"}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "status.json"
            with patch.object(maintenance, "OUT_DIR", Path(directory)), \
                    patch.object(maintenance, "OUT_FILE", output), \
                    patch.object(maintenance, "TIKTOK_NEXT_REFRESH_FILE", Path(directory) / "token.next"), \
                    patch.object(maintenance, "refresh_tiktok_access", return_value=("fixture-token" if connected else None, service)), \
                    patch.object(maintenance, "list_tiktok_all", return_value=(list(available.values()), list_error)), \
                    patch.object(maintenance, "query_tiktok_videos", return_value=(available, None)) as query, \
                    patch.dict(maintenance.os.environ, {'GITHUB_SHA': 'a' * 40}), \
                    redirect_stdout(io.StringIO()):
                maintenance.main()
            if connected:
                self.assertEqual(set(query.call_args.args[1]), set(self.by_id))
            else:
                query.assert_not_called()
            return json.loads(output.read_text(encoding="utf-8"))

    def tiktok_rows(self, report):
        return [(item, media) for item in report["items"] for media in item["media"]
                if media.get("provider") == "tiktok"]

    def test_registered_relations_are_checked_and_old_reference_is_not_counted_twice(self):
        report = self.report()
        self.assertEqual(report['revision'], 'a' * 40)
        self.assertTrue(report['tiktok_inventory']['complete'])
        rows = self.tiktok_rows(report)
        self.assertEqual(len(rows), self.expected_relations)
        self.assertEqual(report["summary"]["videos_tiktok"], len(self.by_id))
        self.assertEqual(report["summary"]["relaciones_tiktok"], self.expected_relations)
        self.assertEqual({row["video_id"] for _, row in rows}, set(self.by_id))
        self.assertEqual(len({(item["code"], row["id"]) for item, row in rows}), len(rows))
        self.assertNotIn("fr-pro-01-tiktok-01", {row["id"] for _, row in rows})
        self.assertTrue(all("encontrado" in row["detail"] for _, row in rows))
        self.assertEqual(report["summary"]["recursos"], 2)  # Solo los dos diagramas internos.
        for item, row in rows:
            self.assertTrue(row["url"].startswith("https://www.tiktok.com/@iskay.app/video/"))
            known = item["code"] == "FR-PRO-01" and row["video_id"] == "7701409317936844054"
            self.assertEqual(row["derived_from_version"], 1 if known else None)
            self.assertEqual(row["reviewed"], "2026-11-01" if known else None)
            if known:
                self.assertEqual(row["version"], 1)
                self.assertEqual(row["status"], "OK")
            elif item["content_version"] is not None:
                self.assertEqual(row["status"], "REVISAR")
                self.assertIn("derived_from_version", row["detail"])

    def test_removed_registered_video_marks_every_affected_ficha(self):
        missing = self.videos[-1]["id"]
        report = self.report(missing=missing)
        affected = [(item, row) for item, row in self.tiktok_rows(report) if row["video_id"] == missing]
        self.assertTrue(affected)
        for item, row in affected:
            self.assertEqual(row["status"], "ROTO")
            self.assertEqual(item["status"], "ROTO")
            self.assertIn("no devolvió", row["detail"])
            self.assertTrue(row["url"].startswith("https://www.tiktok.com/@iskay.app/video/"))

    def test_unavailable_service_does_not_silently_approve_registered_videos(self):
        report = self.report(connected=False)
        self.assertFalse(report['tiktok_inventory']['complete'])
        rows = self.tiktok_rows(report)
        self.assertEqual(len(rows), self.expected_relations)
        self.assertTrue(all(row["status"] != "OK" for _, row in rows))
        self.assertTrue(all("Servicio simulado" in row["detail"] for _, row in rows))

    def test_partial_inventory_retains_rows_without_claiming_completeness(self):
        report = self.report(list_error='La segunda página no respondió')
        self.assertFalse(report['tiktok_inventory']['complete'])
        self.assertEqual(report['services']['tiktok']['status'], 'ROTO')
        self.assertEqual(len(report['tiktok_inventory']['videos']), len(self.videos))


if __name__ == "__main__":
    unittest.main()
