"""Contratos del ensamblaje editorial aprobado (independiente de multimedia)."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import build_share_catalog as share


class ApprovedFrAssemblyTests(unittest.TestCase):
    def setUp(self):
        self.example = {
            "schema_version": 1,
            "category": "Financiamiento Reembolsable",
            "category_code": "FR",
            "source": "5.1 Aprobacion_calendario_Financiamiento_Reembolsable_iskay.xlsm",
            "approved_on": "2026-11-04",
            "approval": "ensamblaje correcto - aprobado",
            "expected_pieces": 2,
            "expected_relations": 3,
            "pieces": [
                {
                    "code": "PRO-EDU-01", "title": "Primera pieza",
                    "role": "Promotores", "principal": ["FR-PRO-01"],
                    "complementaria": ["FR-PRO-02"],
                },
                {
                    "code": "PRO-EDU-02", "title": "Segunda pieza",
                    "role": "Promotores", "principal": ["FR-PRO-01"],
                    "complementaria": [],
                },
            ],
        }

    def sample_catalog(self):
        return [
            {"code": "FR-PRO-01", "role": "promotores",
             "category": "Financiamiento Reembolsable", "marketing_pieces": [], "media": []},
            {"code": "FR-PRO-02", "role": "Promotores",
             "category": "Financiamiento Reembolsable", "marketing_pieces": [], "media": []},
        ]

    def run_case(self, data):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "_data").mkdir()
            (root / "_data/fr_ensamblaje_marketing.json").write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8"
            )
            catalog = self.sample_catalog()
            errors = []
            with patch.object(share, "ROOT", root):
                report = share.apply_approved_assembly(catalog, errors)
            return report, catalog, errors

    def test_many_to_many_is_explicit_without_inventing_assets(self):
        report, entries, errors = self.run_case(self.example)
        self.assertEqual(errors, [])
        self.assertEqual(report["pieces"], 2)
        self.assertEqual(report["relations"], 3)
        self.assertEqual(report["principal"], 2)
        self.assertEqual(report["complementaria"], 1)
        self.assertEqual(report["linked_fichas"], 2)
        first = entries[0]["editorial_pieces"]
        self.assertEqual([p["code"] for p in first], ["PRO-EDU-01", "PRO-EDU-02"])
        self.assertTrue(all(p["relation"] == "Principal" for p in first))
        self.assertEqual(entries[1]["editorial_pieces"][0]["relation"], "Complementaria")
        self.assertEqual(entries[0]["marketing_pieces"], [])
        self.assertEqual(entries[0]["media"], [])
        self.assertTrue(all("assets" not in piece and "media_url" not in piece
                            for entry in entries for piece in entry["editorial_pieces"]))

    def test_missing_ficha_different_role_and_duplicate_are_rejected(self):
        data = json.loads(json.dumps(self.example))
        data["pieces"][0]["principal"].append("CF-FR-INV-001")
        data["pieces"][1]["complementaria"].append("FR-PRO-01")
        _, _, errors = self.run_case(data)
        self.assertTrue(any("inexistente" in error for error in errors))
        self.assertTrue(any("duplicada" in error for error in errors))

        data = json.loads(json.dumps(self.example))
        data["pieces"][0]["role"] = "Inversores"
        _, _, errors = self.run_case(data)
        self.assertTrue(any("código o rol" in error for error in errors))

    def test_unauthorized_assembly_is_not_silently_accepted(self):
        data = json.loads(json.dumps(self.example))
        data["approval"] = "pendiente"
        report, _, errors = self.run_case(data)
        self.assertIsNone(report)
        self.assertTrue(any("aprobación" in e for e in errors))

    def test_repository_data_keeps_approved_counts_and_exception_codes(self):
        path = Path(__file__).resolve().parents[1] / "_data/fr_ensamblaje_marketing.json"
        if not path.exists():
            self.skipTest("La fuente de ensamblaje aún no se ha instalado")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["approval"], "ensamblaje correcto - aprobado")
        self.assertEqual(data["approved_on"], "2026-11-04")
        self.assertEqual(len(data["pieces"]), 61)
        self.assertEqual(sum(map(lambda p: len(p["principal"]), data["pieces"])), 93)
        self.assertEqual(sum(map(lambda p: len(p["complementaria"]), data["pieces"])), 92)
        self.assertEqual({p["code"] for p in data["pieces"] if not p["principal"]},
                         {"INV-EDU-05", "COL-VEN-02"})


if __name__ == "__main__":
    unittest.main()
