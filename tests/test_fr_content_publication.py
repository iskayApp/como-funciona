"""Integridad de publicación de los tres roles de Financiamiento Reembolsable."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
FR = ROOT / "ideas" / "financiamiento-reembolsable"


def metadata(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\\n"):
        return {}, text
    _, front, body = text.split("---\\n", 2)
    return yaml.safe_load(front) or {}, body


class FRCrossRolePublication(unittest.TestCase):
    def test_three_roles_and_99_unique_codes(self):
        pages = [metadata(path)[0] for path in FR.rglob("*.md")]
        codes = [p["code"] for p in pages if p.get("code")]
        self.assertEqual(len(codes), 99)
        self.assertEqual(len(set(codes)), len(codes))
        self.assertEqual(sum(code.startswith("FR-PRO-") for code in codes), 33)
        self.assertEqual(sum(code.startswith("CF-FR-INV-") for code in codes), 37)
        self.assertEqual(sum(code.startswith("CF-FR-COL-") for code in codes), 29)

    def test_new_roles_have_unique_routes_and_review_flags(self):
        docs = []
        all_routes = set()
        for path in FR.rglob("*.md"):
            meta, body = metadata(path)
            if meta.get("permalink"):
                self.assertNotIn(meta["permalink"], all_routes)
                all_routes.add(meta["permalink"])
            if str(meta.get("code", "")).startswith(("CF-FR-INV-", "CF-FR-COL-")):
                docs.append((meta, body))
                self.assertEqual(meta.get("status"), "published")
                self.assertIs(meta.get("published"), True)
                self.assertIn(meta.get("editorial_status"), ("approved", "pending_review"))
                self.assertEqual(meta.get("content_version"), 1)
                self.assertIn("Respuesta breve", body)
                if meta["editorial_status"] == "pending_review":
                    self.assertIn("Pendiente de revisión editorial", body)
                    self.assertIs(meta["reviewed"], False)
        self.assertEqual(len(docs), 66)
        self.assertEqual(sum(m["editorial_status"] == "approved" for m, _ in docs), 7)
        self.assertEqual(sum(m["editorial_status"] == "pending_review" for m, _ in docs), 59)
        for meta, _ in docs:
            for field in ("prev_url", "next_url", "stage_url"):
                if meta.get(field):
                    self.assertIn(meta[field], all_routes, (meta["code"], field))

    def test_noindex_stays_enabled(self):
        config = yaml.safe_load((ROOT / "_config.yml").read_text(encoding="utf-8"))
        self.assertIs(config["noindex"], True)
        self.assertNotIn("ideas/financiamiento-reembolsable/index.md", config.get("exclude", []))

if __name__ == "__main__":
    unittest.main()
