"""Save the one-page site as a single HTML file that opens with a double-click.

Styles, script, fonts, logo and every photo are built into the file, so it
needs no server. Only the map, the messenger links and the route link need
the internet. The language switch is left out because it needs the server.

    python manage.py export_html                # Russian, pushka-hotel.html
    python manage.py export_html --lang en -o pushka-hotel-en.html
"""

import base64
import io
import mimetypes
import re
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from django.utils import translation
from PIL import Image

FULL_SIZE = 1280  # longest side of a photo in the viewer
FULL_QUALITY = 72


def data_uri(raw, mime):
    return "data:%s;base64,%s" % (mime, base64.b64encode(raw).decode("ascii"))


def file_uri(path):
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    if path.suffix == ".woff2":
        mime = "font/woff2"
    return data_uri(path.read_bytes(), mime)


def photo_uri(path):
    with Image.open(path) as img:
        img = img.convert("RGB")
        img.thumbnail((FULL_SIZE, FULL_SIZE))
        out = io.BytesIO()
        img.save(out, "JPEG", quality=FULL_QUALITY, optimize=True, progressive=True)
    return data_uri(out.getvalue(), "image/jpeg")


class Command(BaseCommand):
    help = "Save the site as one self-contained HTML file."

    def add_arguments(self, parser):
        parser.add_argument("--lang", default="ru", choices=[c for c, _ in settings.LANGUAGES])
        parser.add_argument("-o", "--output", default=None)

    def handle(self, *args, lang, output, **options):
        output = Path(output or ("pushka-hotel.html" if lang == "ru" else "pushka-hotel-%s.html" % lang))
        host = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS and settings.ALLOWED_HOSTS[0] != "*" else "localhost"
        with translation.override(lang):
            response = Client(HTTP_HOST=host).get("/%s/" % lang)
        if response.status_code != 200:
            raise CommandError("The page returned %s." % response.status_code)
        html = response.content.decode("utf-8")

        static_url = settings.STATIC_URL
        media_url = settings.MEDIA_URL

        def static_path(url):
            found = finders.find(url[len(static_url):])
            if not found:
                raise CommandError("Static file not found: %s" % url)
            return Path(found)

        def media_path(url):
            return Path(settings.MEDIA_ROOT) / url[len(media_url):]

        # Parts that only work with the server running.
        html = re.sub(r'\s*<form class="lang-switch".*?</form>', "", html, flags=re.S)
        html = re.sub(r'\s*<link rel="alternate"[^>]*>', "", html)
        html = re.sub(r'\s*<meta property="og:image"[^>]*>', "", html)
        html = re.sub(r'href="/%s/"' % lang, 'href="#"', html)

        # Stylesheet, with the fonts inside it.
        def inline_css(match):
            css_path = static_path(match.group(1))
            css = css_path.read_text(encoding="utf-8")
            css = re.sub(
                r'url\("(\.\./[^"]+)"\)',
                lambda m: 'url("%s")' % file_uri((css_path.parent / m.group(1)).resolve()),
                css,
            )
            return "<style>\n%s</style>" % css

        html = re.sub(r'<link rel="stylesheet" href="([^"]+)">', inline_css, html)

        # Script, moved to the end of the page because inline scripts cannot be deferred.
        script = ""

        def take_script(match):
            nonlocal script
            script = static_path(match.group(1)).read_text(encoding="utf-8")
            return ""

        html = re.sub(r'\s*<script src="([^"]+)" defer></script>', take_script, html)
        if script:
            html = html.replace("</body>", "<script>\n%s</script>\n</body>" % script)

        # Full-size photos for the viewer, made smaller so the file stays light.
        cache = {}

        def media_uri(url, full):
            if url not in cache:
                path = media_path(url)
                cache[url] = photo_uri(path) if full else file_uri(path)
            return cache[url]

        html = re.sub(
            r'<a href="(%s[^"]+)" data-photo>' % re.escape(media_url),
            lambda m: '<a href="%s" data-photo>' % media_uri(m.group(1), full=True),
            html,
        )
        # Everything else: thumbnails, logo, icon, hero picture.
        html = re.sub(
            r'(%s[^"\')\s]+)' % re.escape(media_url),
            lambda m: media_uri(m.group(1), full=False),
            html,
        )
        html = re.sub(
            r'(%s[^"\')\s]+)' % re.escape(static_url),
            lambda m: file_uri(static_path(m.group(1))),
            html,
        )

        output.write_text(html, encoding="utf-8")
        size = output.stat().st_size / 1024 / 1024
        self.stdout.write(self.style.SUCCESS("Saved %s (%.1f MB)." % (output, size)))
