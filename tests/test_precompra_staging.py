"""Garantiza que las 66 fichas de Precompra sigan en borrador fuera del sitio."""
from collections import Counter
from pathlib import Path
import re
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ".github" / "staging" / "precompra" / "ideas" / "precompra"
ROLES = {"Promotores": 36, "Precompradores": 21, "Colaboradores": 9}
STAGES = {"Promotores": 9, "Precompradores": 6, "Colaboradores": 4}
REVIEW_DATE = "2026-11-14"
GUIDE_SOURCE = "https://docs.google.com/document/d/1_wX6OGVxUrs3I9WF-hDgWiB8MWv9Ysfy/edit"

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
        self.assertEqual(len({x["editorial_source_url"] for x in items}), 66)

    def test_content_version_snapshot_after_2026_11_14_review(self):
        # Instantánea de esta revisión: solo 42 fichas cambiaron funcionalmente.
        # El contraste de metadatos de las otras 24 no incrementa su versión.
        versions = []
        for path, data, _ in self.cards:
            with self.subTest(path=str(path)):
                self.assertIs(type(data["content_version"]), int)
                self.assertGreater(data["content_version"], 0)
                versions.append(data["content_version"])
        self.assertEqual(Counter(versions), {1: 24, 2: 42})

    def test_functional_review_is_separate_from_editorial_approval(self):
        for path, data, _ in self.cards:
            with self.subTest(path=str(path)):
                self.assertEqual(data["functional_review_status"], "completed")
                self.assertEqual(data["functional_reviewed_on"], REVIEW_DATE)
                self.assertEqual(data["source_checked_on"], REVIEW_DATE)
                self.assertEqual(data["guide_review_closed_on"], REVIEW_DATE)
                self.assertEqual(data["guide_source_url"], GUIDE_SOURCE)
                self.assertEqual(data["guide_version"], "No indicada expresamente")
                self.assertEqual(data["editorial_status"], "pending_review")
                self.assertIs(data["reviewed"], False)
                self.assertNotEqual(data["editorial_source_url"], data["guide_source_url"])

    def test_description_matches_the_brief_answer(self):
        for path, data, body in self.cards:
            with self.subTest(path=str(path)):
                brief = re.search(r"^## Respuesta breve\n+(.*?)(?=\n## |\Z)", body, re.M | re.S)
                self.assertIsNotNone(brief)
                self.assertTrue(brief.group(1).strip())
                self.assertEqual(data["description"], brief.group(1).strip())

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
        self.assertEqual(list((ROOT / "ideas" / "precompra").rglob("cf-pre-*.md")), [])
        categories = yaml.safe_load((ROOT / "_data/categories.yml").read_text(encoding="utf-8"))
        precompra = next(item for item in categories if item["id"] == "precompra")
        self.assertEqual(precompra["status"], "preparation")
        self.assertEqual(precompra["roles"], [])
        indexes = list(BASE.rglob("index.md"))
        self.assertEqual(len(indexes), 23)
        self.assertEqual(len(list(BASE.glob("*/index.md"))), 3)
        self.assertEqual(len(list(BASE.glob("*/*/index.md"))), 19)
        for p in indexes:
            data, _ = metadata(p)
            with self.subTest(index=str(p)):
                self.assertEqual(data["category"], "Precompra")
                self.assertIs(data["published"], False)
                self.assertEqual(data["status"], "draft")
                self.assertEqual(data["visibility"], "private")
                self.assertEqual(data["publication_status"], "not_published")
                self.assertEqual(data["editorial_status"], "pending_review")
                self.assertIs(data["reviewed"], False)

    def test_navigation_is_contiguous_and_role_specific(self):
        items = [data for _, data, _ in self.cards]
        stages = {data["stage_id"]: data for data, _ in
                  (metadata(path) for path in BASE.glob("*/*/index.md"))}
        self.assertEqual(len(stages), 19)
        for role in ROLES:
            ordered = sorted((x for x in items if x["role"] == role), key=lambda x:x["code"])
            for i, entry in enumerate(ordered):
                previous = ordered[i-1] if i else None
                following = ordered[i+1] if i+1 < len(ordered) else None
                self.assertEqual(entry["prev_code"], previous["code"] if previous else None)
                self.assertEqual(entry["prev_url"], previous["permalink"] if previous else None)
                self.assertEqual(entry["prev_title"], previous["title"] if previous else None)
                self.assertEqual(entry["next_code"], following["code"] if following else None)
                self.assertEqual(entry["next_url"], following["permalink"] if following else None)
                self.assertEqual(entry["next_title"], following["title"] if following else None)
                self.assertEqual(entry["stage_url"].startswith(f"/precompra/{entry['role'].lower()}/"), True)
                self.assertIn(entry["stage_id"], stages)
                stage = stages[entry["stage_id"]]
                self.assertEqual(entry["stage_url"], stage["permalink"])
                self.assertEqual(entry["role"], stage["role"])
                self.assertEqual(entry["stage"], stage["stage"])

if __name__ == "__main__":
    unittest.main()
