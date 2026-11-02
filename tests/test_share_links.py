import unittest

from scripts.build_share_catalog import original_url, public_url, slugify, valid_http_url


CONFIG = {"url": "https://iskayapp.github.io", "baseurl": "/como-funciona"}


class ShareLinkTests(unittest.TestCase):
    def test_canonical_and_internal_resource_use_baseurl(self):
        self.assertEqual(
            public_url(CONFIG, "/financiamiento-reembolsable/promotores/tema/"),
            "https://iskayapp.github.io/como-funciona/financiamiento-reembolsable/promotores/tema/",
        )
        self.assertEqual(
            original_url({"storage": "internal", "src": "/assets/ejemplo.svg"}, CONFIG),
            "https://iskayapp.github.io/como-funciona/assets/ejemplo.svg",
        )

    def test_youtube_uses_video_id_without_manual_url(self):
        self.assertEqual(
            original_url({"storage": "external", "provider": "youtube", "video_id": "aBc_123-Z"}, CONFIG),
            "https://www.youtube.com/watch?v=aBc_123-Z",
        )

    def test_tiktok_uses_original_share_url(self):
        self.assertEqual(
            original_url({"provider": "tiktok", "video_id": "123", "share_url": "https://www.tiktok.com/@iskay/video/123"}, CONFIG),
            "https://www.tiktok.com/@iskay/video/123",
        )
        self.assertIsNone(original_url({"provider": "tiktok", "video_id": "123"}, CONFIG))

    def test_unavailable_and_unsafe_schemes_do_not_generate_originals(self):
        self.assertFalse(valid_http_url("javascript:alert(1)"))
        self.assertIsNone(original_url({"storage": "external", "src": "javascript:alert(1)"}, CONFIG))
        self.assertIsNone(original_url({"storage": "internal", "src": "/secret.txt"}, CONFIG))

    def test_anchor_is_deterministic(self):
        self.assertEqual(slugify("fr-pro-09-flujo-pagos"), "fr-pro-09-flujo-pagos")


if __name__ == "__main__":
    unittest.main()
