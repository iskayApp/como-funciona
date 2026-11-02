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

    def test_explicit_production_code_groups_approved_assets(self):
        metadata = """
code: FR-PRO-07
title: Una ficha con dos piezas
permalink: /ficha-07/
distribution:
  facebook:
    - id: fb-01
      status: published
      url: https://www.facebook.com/reel/123456
    - id: fb-02
      status: approved
      url: https://www.facebook.com/reel/987654
  tiktok:
    - id: tt-01
      status: published
      share_url: https://www.tiktok.com/@iskay/video/123
    - id: tt-sin-relacion
      status: published
      share_url: https://www.tiktok.com/@iskay/video/999
marketing_pieces:
  - code: PRO-EDU-02
    category_code: FR
    title: Algunas condiciones dependen del monto
    status: approved
    asset_ids: [fb-01, tt-01]
  - code: PRO-INS-02
    category_code: FR
    title: Historia de un promotor
    status: approved
    asset_ids: [fb-02]
"""
        code, data = self.build_with(metadata)
        self.assertEqual(code, 0)
        item = data["items"][0]
        self.assertEqual(data["total_marketing_pieces"], 2)
        self.assertEqual(data["total_unassigned_assets"], 1)
        self.assertEqual([piece["code"] for piece in item["marketing_pieces"]],
                         ["PRO-EDU-02", "PRO-INS-02"])
        self.assertEqual([asset["id"] for asset in item["marketing_pieces"][0]["assets"]],
                         ["fb-01", "tt-01"])
        self.assertEqual(item["unassigned_assets"][0]["id"], "tt-sin-relacion")
        self.assertEqual(item["marketing_pieces"][0]["category_code"], "FR")

    def test_does_not_infer_marketing_code_from_asset_id(self):
        metadata = """
code: FR-PRO-01
title: Identificadores diferentes
permalink: /concepto/
distribution:
  tiktok:
    - id: fr-pro-01-tiktok-01
      status: published
      share_url: https://www.tiktok.com/@iskay/video/123
"""
        code, data = self.build_with(metadata)
        self.assertEqual(code, 0)
        item = data["items"][0]
        self.assertEqual(item["marketing_pieces"], [])
        self.assertEqual(item["unassigned_assets"][0]["id"], "fr-pro-01-tiktok-01")

    def test_invalid_explicit_link_fails_build_instead_of_inventing_relation(self):
        metadata = """
code: FR-PRO-05
title: Referencia inexistente
permalink: /otro/
marketing_pieces:
  - code: PRO-EDU-01
    category_code: FR
    title: Un ejemplo
    status: approved
    asset_ids: [publicacion-que-no-existe]
"""
        code, data = self.build_with(metadata)
        self.assertEqual(code, 1)
        self.assertEqual(data["items"][0]["marketing_pieces"][0]["assets"], [])

    def test_unpublished_piece_never_leaks_to_public_catalog(self):
        metadata = """
code: FR-PRO-04
title: Una ficha
permalink: /ficha/
distribution:
  facebook:
    - id: fb-public
      status: approved
      url: https://www.facebook.com/reel/123456
marketing_pieces:
  - code: PRO-EDU-15
    category_code: FR
    title: Reservada
    status: draft
    asset_ids: [fb-public]
"""
        code, data = self.build_with(metadata)
        self.assertEqual(code, 0)
        self.assertEqual(data["items"][0]["marketing_pieces"], [])
        self.assertEqual(len(data["items"][0]["unassigned_assets"]), 1)


    def test_public_search_uses_the_existing_catalog_and_can_hide_drafts(self):
        cases = [
            ("", True),
            ("published: false", False),
            ("visibility: private", False),
            ("status: draft", False),
            ("status: review", False),
            ("status: archived", False),
            ("status: approved", True),
        ]
        for extra, expected in cases:
            with self.subTest(extra=extra):
                metadata = (
                    "code: FR-PRO-01\n"
                    "title: ¿Qué es el financiamiento?\n"
                    "permalink: /pregunta-publica/\n"
                    "category: Financiamiento Reembolsable\n"
                    "role: promotores\n"
                    "stage: Antes de solicitar\n"
                    + extra
                )
                code, data = self.build_with(metadata)
                self.assertEqual(code, 0)
                item = data["items"][0]
                self.assertEqual(item["public_searchable"], expected)
                self.assertEqual(item["code"], "FR-PRO-01")
                self.assertEqual(item["stage"], "Antes de solicitar")
                self.assertTrue(item["canonical_url"].endswith("/pregunta-publica/"))



if __name__ == "__main__":
    unittest.main()
