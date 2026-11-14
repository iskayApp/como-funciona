"""Trazabilidad de fichas públicas y controles documentales de Precompra."""
import json
from pathlib import Path
import unittest
from collections import Counter, defaultdict
import yaml

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / ".github" / "staging" / "precompra"
FICHAS = ROOT / "ideas" / "precompra"
REVIEW_DATE = "2026-11-14"
GUIDE_SOURCE = "https://docs.google.com/document/d/1_wX6OGVxUrs3I9WF-hDgWiB8MWv9Ysfy/edit"

def read_json(name):
    return json.loads((STAGING / name).read_text(encoding="utf-8"))

def card_meta(path):
    data = path.read_text(encoding="utf-8")
    return yaml.safe_load(data.split("---", 2)[1])

class PrecompraControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = {meta["code"]: meta for meta in (card_meta(path) for path in FICHAS.rglob("cf-pre-*.md"))}

    def test_classification_matrix_and_full_reference_coverage(self):
        data = read_json("clasificacion.json")
        rows = data["records"]
        ids = {row["id"] for row in rows}
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["category"], "Precompra")
        self.assertEqual(data["record_status"], "functional_review_completed_editorial_pending")
        self.assertEqual(data["guide_source"], GUIDE_SOURCE)
        self.assertEqual(data["guide_version"], "No indicada expresamente")
        self.assertEqual(data["functional_review_status"], "completed")
        for field in ("guide_review_closed_on", "source_checked_on", "functional_reviewed_on"):
            self.assertEqual(data[field], REVIEW_DATE)
        self.assertEqual(len(rows), 116)
        self.assertEqual(len(ids), len(rows))
        self.assertEqual(ids, {f"CL-PRE-{i:03}" for i in range(1, 117)})
        self.assertEqual(data["counts"]["records"], len(rows))
        self.assertEqual(data["counts"]["types"], Counter(row["type"] for row in rows))
        for row in rows:
            with self.subTest(classification=row["id"]):
                self.assertIn(row["type"], {"CON", "COND", "DER", "OBL", "FAC", "EST", "PRO", "RIES"})
                for field in ("actor", "text", "source_section"):
                    self.assertIsInstance(row[field], str)
                    self.assertTrue(row[field].strip())
        referenced = set()
        for code, card in self.cards.items():
            with self.subTest(code=code):
                self.assertTrue(card["classification_refs"])
                for field in ("classification_refs", "classification_secondary_refs"):
                    refs = card[field]
                    self.assertIsInstance(refs, list)
                    self.assertEqual(len(refs), len(set(refs)))
                    self.assertLessEqual(set(refs), ids)
                    referenced.update(refs)
        self.assertEqual(referenced, ids)

    def test_observations_have_exact_traceability(self):
        data = read_json("observaciones.json")
        rows = data["observations"]
        self.assertEqual(len(rows), 8)
        ids = {f"OBS-PRE-{i:02}" for i in range(1, 9)}
        resolved = {"OBS-PRE-01", "OBS-PRE-02", "OBS-PRE-03", "OBS-PRE-08"}
        self.assertEqual({x["id"] for x in rows}, ids)
        self.assertEqual(data["record_status"], "functional_review_completed_editorial_pending")
        self.assertEqual(data["guide_source"], GUIDE_SOURCE)
        self.assertTrue(data["guide_modification_scope"].strip())
        for field in ("guide_review_closed_on", "source_checked_on", "functional_reviewed_on"):
            self.assertEqual(data[field], REVIEW_DATE)
        by_code = defaultdict(set)
        for code, card in self.cards.items():
            for observation in card["observation_refs"]:
                by_code[observation].add(code)
        self.assertEqual(set(by_code), ids)
        for entry in rows:
            with self.subTest(id=entry["id"]):
                self.assertEqual(entry["status"], "resolved_in_guide" if entry["id"] in resolved else "criterion_applied")
                self.assertIs(entry["guide_modified"], False)
                self.assertIs(entry["authorized_resolution"], True)
                self.assertEqual(entry["resolution_source"], data["guide_source"])
                self.assertEqual(entry["functional_reviewed_on"], REVIEW_DATE)
                self.assertTrue(entry["sections"])
                self.assertTrue(entry["decision"].strip())
                self.assertEqual(len(entry["affected_codes"]), len(set(entry["affected_codes"])))
                self.assertEqual(set(entry["affected_codes"]), by_code[entry["id"]])

    def test_media_candidates_not_falsely_published_or_linked(self):
        data = read_json("marketing_candidatos.json")
        calendar_snapshot = {"PRE-EDU-01": "Publicada", "PRO-VEN-04": "Publicada", "PRO-ENT-01": "En producción"}
        self.assertEqual(len(data["items"]), 3)
        self.assertEqual(data["public_urls_verified"], 0)
        self.assertEqual({x["code"] for x in data["items"]}, set(calendar_snapshot))
        self.assertEqual(data["reconciled_on"], REVIEW_DATE)
        self.assertTrue(data["review_scope"].strip())
        for item in data["items"]:
            with self.subTest(code=item["code"]):
                self.assertIs(item["social_publication_verified"], False)
                self.assertIsNone(item["facebook_original_url"])
                self.assertIsNone(item["tiktok_original_url"])
                self.assertEqual(item["calendar_status"], calendar_snapshot[item["code"]])
                self.assertEqual(item["candidate_status"], "pending_editorial_and_social_url_verification")
                self.assertTrue(item["production_document"].startswith("https://docs.google.com/document/d/"))
                self.assertTrue(item["candidate_ficha_codes"])
                for code in item["candidate_ficha_codes"]:
                    self.assertIn(code, self.cards)
                    self.assertEqual(self.cards[code]["role"], item["role"])
        for card in self.cards.values():
            self.assertEqual(card["media"], [])
            self.assertEqual(card["distribution"], [])
            self.assertEqual(card["marketing_pieces"], [])

    def test_functions_still_require_operational_proof(self):
        data = read_json("funciones_pendientes.json")
        self.assertEqual(len(data["items"]), 9)
        self.assertEqual({row["id"] for row in data["items"]}, {f"FUNC-PRE-{i:02}" for i in range(1, 10)})
        self.assertEqual(data["status"], "operational_verification_pending")
        self.assertEqual(data["documentation_checked_on"], REVIEW_DATE)
        self.assertEqual(data["guide_source"], GUIDE_SOURCE)
        self.assertTrue(data["review_scope"].strip())
        for row in data["items"]:
            with self.subTest(function=row["id"]):
                self.assertEqual(row["evidence"], "no_verificada")
                self.assertTrue(row["source_section"].strip())
                self.assertTrue(row["followup"].strip())
        self.assertEqual(len(self.cards), 66)

if __name__ == "__main__":
    unittest.main()
