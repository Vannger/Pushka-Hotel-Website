import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase


class ExportHtmlTests(TestCase):
    def test_file_needs_no_server(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "site.html"
            call_command("export_html", output=str(out), stdout=open("/dev/null", "w"))
            html = out.read_text(encoding="utf-8")
        self.assertIn("Время только для вас", html)
        self.assertNotIn("/static/", html)
        self.assertNotIn("lang-switch\"", html)
        self.assertNotIn("csrfmiddlewaretoken", html)
        self.assertIn("data:font/woff2;base64,", html)
        self.assertIn("<style>", html)
