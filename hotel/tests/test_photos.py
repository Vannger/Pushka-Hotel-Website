import json
import shutil
import tempfile
from io import BytesIO, StringIO
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import translation
from PIL import Image

from hotel.models import HotelPhoto, Suite, SuitePhoto


def image_bytes(size, fmt="JPEG", exif_orientation=None):
    img = Image.new("RGB", size, (200, 120, 80))
    buffer = BytesIO()
    kwargs = {}
    if exif_orientation:
        exif = Image.Exif()
        exif[0x0112] = exif_orientation
        kwargs["exif"] = exif.tobytes()
    img.save(buffer, fmt, **kwargs)
    return buffer.getvalue()


class TempMediaMixin:
    def setUp(self):
        super().setUp()
        self.media = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media, ignore_errors=True)
        super().tearDown()


class PhotoProcessingTests(TempMediaMixin, TestCase):
    def test_large_upload_is_resized_and_saved_as_jpeg(self):
        suite = Suite.objects.get(number=2)
        upload = SimpleUploadedFile("IMG_0001.png", image_bytes((4000, 3000), "PNG"))
        photo = SuitePhoto.objects.create(suite=suite, image=upload)
        with Image.open(photo.image.path) as img:
            self.assertEqual(img.format, "JPEG")
            self.assertEqual(max(img.size), 1920)
        self.assertTrue(photo.image.name.startswith("suites/IMG_0001"))
        self.assertTrue(photo.image.name.endswith(".jpg"))
        with Image.open(photo.thumbnail.path) as thumb:
            self.assertEqual(thumb.width, 800)
        self.assertIn("/thumbs/", photo.thumb_url)

    def test_exif_orientation_is_applied_and_removed(self):
        suite = Suite.objects.get(number=2)
        upload = SimpleUploadedFile("phone.jpg", image_bytes((1200, 900), exif_orientation=6))
        photo = SuitePhoto.objects.create(suite=suite, image=upload)
        with Image.open(photo.image.path) as img:
            self.assertEqual(img.size, (900, 1200))
            self.assertFalse(img.info.get("exif"))

    def test_small_clean_jpeg_is_stored_untouched(self):
        data = image_bytes((1600, 1000))
        photo = HotelPhoto.objects.create(image=SimpleUploadedFile("hall.jpg", data))
        self.assertEqual(Path(photo.image.path).read_bytes(), data)
        self.assertTrue(photo.image.name.startswith("hotel/"))
        self.assertTrue(photo.thumbnail)


class LoadPhotosCommandTests(TempMediaMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.source = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.source, ignore_errors=True)
        manifest = {
            "hotel": [{"file": "01.jpg", "alt_ru": "Коридор", "alt_en": "Corridor"}],
            "suite-2": [
                {"file": "01.jpg", "alt_ru": "Кровать", "alt_en": "Bed"},
                {"file": "02.jpg", "alt_ru": "Ванная", "alt_en": "Bathroom"},
            ],
        }
        for group, items in manifest.items():
            (self.source / group).mkdir()
            for item in items:
                (self.source / group / item["file"]).write_bytes(image_bytes((1200, 800)))
        (self.source / "photos.json").write_text(json.dumps(manifest), encoding="utf-8")

    def load(self, *args):
        call_command("load_photos", "--source", str(self.source), *args, stdout=StringIO())

    def test_loads_photos_in_order_with_captions(self):
        self.load()
        photos = list(Suite.objects.get(number=2).photos.all())
        self.assertEqual([p.alt_en for p in photos], ["Bed", "Bathroom"])
        self.assertEqual([p.order for p in photos], [1, 2])
        self.assertEqual(HotelPhoto.objects.get().alt_ru, "Коридор")

    def test_second_run_skips_and_replace_reloads(self):
        self.load()
        self.load()
        self.assertEqual(SuitePhoto.objects.count(), 2)
        self.load("--replace")
        self.assertEqual(SuitePhoto.objects.count(), 2)
        self.assertEqual(HotelPhoto.objects.count(), 1)

    def test_pages_show_the_photos(self):
        self.load()
        suite = Suite.objects.get(number=2)
        with translation.override("en"):
            detail = self.client.get(suite.get_absolute_url())
            home = self.client.get("/en/")
            about = self.client.get("/en/about/")
        self.assertContains(detail, "data-gallery-thumb", count=2)
        self.assertContains(detail, 'alt="Bathroom"')
        # Suites with photos come first on the home page.
        self.assertEqual(home.context["suites"][0], suite)
        self.assertContains(about, "Corridor")
