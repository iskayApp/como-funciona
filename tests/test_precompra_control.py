"""Pruebas de controles no publicables de Precompra."""
import json
from pathlib import Path
import unittest
from collections import defaultdict
import yaml

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / ".github" / "staging" / "precompra"
FICHAS = STAGING / "ideas" / "precompra"

def read_json(name):
    return json.loads((STAGING / name).read_text(encoding="utf-8"))

def card_meta(path):
    data = path.read_text(encoding="utf-8")
    return yaml.safe_load(data.split("---", 2)[1])

class PrecompraControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = {meta["code"]: meta for meta in (card_meta(path) for path in FICHAS.rglob("cf-pre-*.md"))}

    def test_observations_have_exact_traceability(self):
        data = read_json("observaciones.json")
        rows = data["observations"]
        self.assertEqual(len(rows), 8)
        self.assertEqual({x["id"] for x in rows}, {f"OBS-PRE-{i:02}" for i in range(1, 9)})
        by_code = defaultdict(set)
        for code, card in self.cards.items():
            for observation in card["observation_refs"]:
                by_code[observation].add(code)
        for entry in rows:
            with self.subTest(id=entry["id"]):
                self.assertEqual(entry["status"], "open_pending_owner_review")
                self.assertIs(entry["guide_modified"], False)
                self.assertIs(entry["authorized_resolution"], False)
                self.assertTrue(entry["sections"])
                self.assertTrue(entry["decision"])
                self.assertEqual(set(entry["affected_codes"]), by_code[entry["id"]])

    def test_media_candidates_not_falsely_published_or_linked(self):
        data = read_json("marketing_candidatos.json")
        self.assertEqual(len(data["items"]), 3)
        self.assertEqual(data["public_urls_verified"], 0)
        self.assertEqual({x["code"] for x in data["items"]}, {"PRE-EDU-01", "PRO-VEN-04", "PRO-ENT-01"})
        for item in data["items"]:
            with self.subTest(code=item["code"]):
                self.assertFalse(item["social_publication_verified"])
                self.assertIsNone(item["facebook_original_url"])
                self.assertIsNone(item["tiktok_original_url"])
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
        self.assertEqual(len({row["id"] for row in data["items"]}), 9)
        self.assertTrue(all(x["evidence"] == "no_verificada" for x in data["items"]))
        self.assertEqual(data["status"], "operational_verification_pending")
        self.assertEqual(len(self.cards), 66)

if __name__ == "__main__":
    unittest.main()
