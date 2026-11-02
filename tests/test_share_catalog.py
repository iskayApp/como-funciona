"""Pruebas de contratos para el catálogo único de mantenimiento y marketing."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import build_share_catalog as catalog


class ShareCatalogTests(unittest.TestCase):
    def build_with(self, meta, body=""):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ideas = root / "ideas"
            path = ideas / "financiamiento-reembolsable" / "promotores" / "01-ficha.md"
            path.parent.mkdir(parents=True)
            path.write_text("---\n" + meta.strip() + "\n---\n" + body, encoding="utf-8")
            (root / "_config.yml").write_text(
                'url: "https://iskayapp.github.io"\nbaseurl: "/como-funciona"\n',
                encoding="utf-8",
            )
            output = root / "mantenimiento" / "share_catalog.json"
            with patch.object(catalog, "ROOT", root), patch.object(catalog, "IDEAS", ideas), patch.object(catalog, "OUTPUT", output):
                result = catalog.build_catalog()
            return result, json.loads(output.read_text(encoding="utf-8"))

    def test_canonical_media_and_approved_distribution(self):
        metadata = """
code: FR-PRO-01
title: "Qué es el financiamiento"
permalink: /financiamiento-reembolsable/promotores/que-es/
category: Financiamiento reembolsable
role: Promotores
stage: Antes de solicitar
media:
  - id: fr-pro-01-diagrama
    type: diagram
    storage: internal
    src: /assets/fr/diagrama.svg
    status: approved
    derived_from_version: 1
distribution:
  youtube:
    - id: fr-pro-01-youtube
      type: video
      video_id: ABC123xyz
      status: approved
      derived_from_version: 1
  tiktok:
    - id: fr-pro-01-borrador
      status: draft
      share_url: https://www.tiktok.com/@iskay/video/123
"""
        code, data = self.build_with(metadata, '<div id="media-fr-pro-01-diagrama"></div>\n')
        self.assertEqual(code, 0)
        self.assertEqual(data["total_fichas"], 1)
        self.assertEqual(data["total_media"], 1)
        self.assertEqual(data["total_distribution"], 1)
        entry = data["items"][0]
        canonical = "https://iskayapp.github.io/como-funciona/financiamiento-reembolsable/promotores/que-es/"
        self.assertEqual(entry["canonical_url"], canonical)
        self.assertEqual(entry["media"][0]["media_url"], canonical + "#media-fr-pro-01-diagrama")
        self.assertEqual(entry["distribution"][0]["original_url"], "https://www.youtube.com/watch?v=ABC123xyz")
        self.assertIsNone(entry["distribution"][0]["media_url"])

    def test_private_and_unapproved_assets_are_not_shared(self):
        metadata = """
code: FR-PRO-02
title: Otra ficha
permalink: /otra/
media:
  - id: oculto
    status: approved
    visibility: private
distribution:
  tiktok:
    - id: borrador
      status: review
      share_url: https://www.tiktok.com/@iskay/video/100
    - id: publico
      status: approved
      share_url: https://www.tiktok.com/@iskay/video/200
"""
        code, data = self.build_with(metadata)
        self.assertEqual(code, 0)
        self.assertEqual(data["total_media"], 0)
        self.assertEqual(data["total_distribution"], 1)
        self.assertEqual(data["items"][0]["distribution"][0]["id"], "publico")

    def test_missing_original_disables_copy_instead_of_inventing_url(self):
        metadata = """
code: FR-PRO-03
title: Sin enlace externo
permalink: /sin-enlace/
distribution:
  tiktok:
    - video_id: "7701409317936844054"
      status: approved
"""
        code, data = self.build_with(metadata)
        self.assertEqual(code, 0)
        resource = data["items"][0]["distribution"][0]
        self.assertIsNone(resource["original_url"])
        self.assertFalse(resource["original_available"])
        self.assertIsNone(resource["media_url"])


if __name__ == "__main__":
    unittest.main()
