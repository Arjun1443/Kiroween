import json
import threading
import unittest
from urllib.request import Request, urlopen
from unittest.mock import patch
from http.server import ThreadingHTTPServer

from app import Article, DEMO, Handler, normalize, restore


class RestorationTests(unittest.TestCase):
    def test_normalizes_and_drops_fragment(self):
        self.assertEqual(normalize("https://EXAMPLE.com:443/a?q=b#note"), "https://example.com/a?q=b")

    def test_rejects_unsupported_addresses(self):
        for value in ["file:///x", "https://localhost/", "https://127.0.0.1",
                      "https://user@example.com", "https://example.com:8000", "https://a.local", "https://example.com/a b"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize(value)

    def test_normalization_idempotence(self):
        for scheme in ("http", "https"):
            for host in ("example.org", "www.Example.net", "bücher.example"):
                for path in ("/", "/topic/page", "/%20?q=abc#ref"):
                    first = normalize(f"{scheme}://{host}{path}")
                    self.assertEqual(normalize(first), first)

    def test_sample_citations_and_dates(self):
        result = restore(DEMO)
        self.assertTrue(result["demo"])
        self.assertEqual(result["captured"], "2021-04-17")
        self.assertEqual(result["published"], "2021-04-12")
        for id_ in result["highlights"]:
            self.assertIn(id_, {item["id"] for item in result["evidence"]})

    def test_extraction_ignores_hidden_markup(self):
        article = Article()
        article.feed("<script>hidden</script><nav><p>Menu text should never appear in any citation item.</p></nav>"
                     "<p>Readable content from the archived historical page.</p>")
        self.assertEqual(article.paragraphs, ["Readable content from the archived historical page."])

    @patch("app.health", return_value="dead")
    @patch("app.build_opener")
    def test_missing_snapshot(self, opener, _health):
        opener.return_value.open.return_value.__enter__.return_value.read.return_value = b"{}"
        self.assertEqual(restore("https://example.com/").get("state"), "missing")

    @patch("app.health", return_value="dead")
    @patch("app.build_opener")
    @patch("app.archive_fetch", side_effect=TimeoutError)
    def test_partial_snapshot(self, _fetch, opener, _health):
        capture = {"closest": {"available": True, "status": "200", "timestamp": "20210112115500"}}
        opener.return_value.open.return_value.__enter__.return_value.read.return_value = json.dumps(
            {"archived_snapshots": capture}).encode()
        self.assertEqual(restore("https://example.com/").get("state"), "partial")

    def test_http_application(self):
        with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
            threading.Thread(target=server.serve_forever, daemon=True).start()
            try:
                base = f"http://127.0.0.1:{server.server_port}"
                with urlopen(base) as response:
                    self.assertIn(b"Tombstone", response.read())
                request = Request(base + "/api/restore", data=json.dumps({"url": DEMO}).encode(),
                                  headers={"Content-Type": "application/json"})
                with urlopen(request) as response:
                    self.assertEqual(json.load(response)["state"], "restored")
            finally:
                server.shutdown()
