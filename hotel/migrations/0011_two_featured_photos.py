"""Add the two photos shown before "Show all photos" to a site that already has photos.

A fresh site gets them from photos/photos.json through load_photos instead,
because load_photos skips suites that already have photos.
"""

from pathlib import Path

from django.conf import settings
from django.db import migrations

PHOTOS = [
    # suite number, file in photos/, Russian caption, English caption, order
    (5, "suite-5/12.jpg", "Кровать у окна", "Bed by the window", 12),
    (6, "suite-6/13.jpg", "Кровать с мягким изголовьем", "Bed with an upholstered headboard", 13),
]


def forwards(apps, schema_editor):
    from django.core.files.base import ContentFile
    from django.core.files.storage import default_storage

    from hotel import images

    Suite = apps.get_model("hotel", "Suite")
    SuitePhoto = apps.get_model("hotel", "SuitePhoto")
    source = Path(settings.BASE_DIR) / "photos"
    for number, rel, alt_ru, alt_en, order in PHOTOS:
        suite = Suite.objects.filter(number=number).first()
        path = source / rel
        if suite is None or not path.exists() or not SuitePhoto.objects.filter(suite=suite).exists():
            continue
        data = path.read_bytes()
        main, thumb = images.prepare(data)
        stem = "suite-%d-%s" % (number, Path(rel).stem)
        image_name = default_storage.save("suites/%s.jpg" % stem, main or ContentFile(data))
        thumb_name = default_storage.save("suites/thumbs/%s-thumb.jpg" % stem, thumb)
        SuitePhoto.objects.create(
            suite=suite, image=image_name, thumbnail=thumb_name,
            alt_ru=alt_ru, alt_en=alt_en, order=order, featured=True,
        )


class Migration(migrations.Migration):
    dependencies = [("hotel", "0010_suitephoto_featured")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
