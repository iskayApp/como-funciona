"""Garantiza que las 66 fichas de Precompra sigan en borrador fuera del sitio."""
from collections import Counter
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "ideas" / "precompra"
ROLES = {"Promotores": 36, "Precompradores": 21, "Colaboradores": 9}
STAGES = {"Promotores": 9, "Precompradores": 6, "Colaboradores": 4}

def metadata(path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), path
    end = text.find("\n---\n", 4)
    assert end > 0, path
    return yaml.safe_load(text[4:end]), text[end + 5:]

class PrecompraStagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = [(p, *metadata(p)) for p in sorted(BASE.rglob("cf-pre-*.md"))]

    def test_count_and_stage_inventory(self):
        self.assertEqual(len(self.cards), 66)
        items = [data for _, data, _ in self.cards]
        self.assertEqual(Counter(x["role"] for x in items), ROLES)
        self.assertEqual(len({x["stage_id"] for x in items}), 19)
        self.assertEqual(Counter({role: len({x["stage_id"] for x in items if x["role"] == role}) for role in ROLES}), Counter(STAGES))
        self.assertEqual(len({x["code"] for x in items}), 66)
        self.assertEqual(len({x["permalink"] for x in items}), 66)
        refs = {ref for x in items for ref in x["classification_refs"]}
        self.assertEqual(refs, {f"CL-PRE-{i:03}" for i in range(1, 109)})

    def test_all_fichas_are_review_pending_and_unpublished(self):
        for path, data, body in self.cards:
            with self.subTest(path=str(path)):
                self.assertEqual(data["category"], "Precompra")
                self.assertEqual(data["status"], "draft")
                self.assertEqual(data["publication_status"], "not_published")
                self.assertEqual(data["editorial_status"], "pending_review")
                self.assertIs(data["published"], False)
                self.assertIs(data["reviewed"], False)
                self.assertEqual(data["visibility"], "private")
                self.assertEqual(data["content_version"], 1)
                self.assertEqual(data["guide_version"], "No indicada expresamente")
                self.assertTrue(data["source"].startswith("1 Precompra.docx"))
                self.assertTrue(data["editorial_source_url"].startswith("https://docs.google.com/document/d/"))
                self.assertEqual(data["media"], [])
                self.assertEqual(data["marketing_pieces"], [])
                self.assertEqual(data["distribution"], [])
                self.assertTrue(data["permalink"].startswith("/precompra/"))
                self.assertIn("## Respuesta breve", body)
                self.assertIn("## Explicación", body)
                self.assertIn("## Qué debes hacer", body)
                self.assertIn("## Siguiente paso", body)

    def test_safeguards_prevent_publication(self):
        config = yaml.safe_load((ROOT / "_config.yml").read_text(encoding="utf-8"))
        self.assertIn("ideas/precompra", config["exclude"])
        categories = yaml.safe_load((ROOT / "_data/categories.yml").read_text(encoding="utf-8"))
        precompra = next(item for item in categories if item["id"] == "precompra")
        self.assertEqual(precompra["status"], "preparation")
        self.assertEqual(precompra["roles"], [])
        for p in [BASE / "index.md", *(BASE / slug / "index.md" for slug in ("promotores", "precompradores", "colaboradores"))]:
            data, _ = metadata(p)
            self.assertIs(data["published"], False)
            self.assertEqual(data["status"], "draft")
            self.assertEqual(data["visibility"], "private")
        self.assertEqual(len(list(BASE.glob("*/*/index.md"))), 19)
        for p in BASE.glob("*/*/index.md"):
            data, _ = metadata(p)
            self.assertIs(data["published"], False)
            self.assertEqual(data["status"], "draft")

    def test_navigation_is_contiguous_and_role_specific(self):
        items = [data for _, data, _ in self.cards]
        for role in ROLES:
            ordered = sorted((x for x in items if x["role"] == role), key=lambda x:x["code"])
            for i, entry in enumerate(ordered):
                previous = ordered[i-1] if i else None
                following = ordered[i+1] if i+1 < len(ordered) else None
                self.assertEqual(entry["prev_code"], previous["code"] if previous else None)
                self.assertEqual(entry["prev_url"], previous["permalink"] if previous else None)
                self.assertEqual(entry["next_code"], following["code"] if following else None)
                self.assertEqual(entry["next_url"], following["permalink"] if following else None)
                self.assertEqual(entry["stage_url"].startswith(f"/precompra/{entry['role'].lower()}/"), True)

if __name__ == "__main__":
    unittest.main()
