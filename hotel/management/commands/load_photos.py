import json
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from hotel.models import HotelPhoto, Suite, SuitePhoto


class Command(BaseCommand):
    help = (
        "Load the hotel and suite photos from the photos/ folder (see photos/photos.json). "
        "Suites that already have photos are skipped unless --replace is given."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            default=str(Path(settings.BASE_DIR) / "photos"),
            help="Folder with photos.json and one subfolder per group.",
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Delete the photos already on the site for each group before loading.",
        )

    def handle(self, *args, source, replace, **options):
        source = Path(source)
        manifest_path = source / "photos.json"
        if not manifest_path.exists():
            raise CommandError(f"{manifest_path} not found.")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        for group, items in manifest.items():
            if group == "hotel":
                existing = HotelPhoto.objects.all()
                make = HotelPhoto
                extra = {}
            elif group.startswith("suite-"):
                try:
                    suite = Suite.objects.get(number=int(group.removeprefix("suite-")))
                except (ValueError, Suite.DoesNotExist):
                    self.stderr.write(f"{group}: no such suite, skipped.")
                    continue
                existing = SuitePhoto.objects.filter(suite=suite)
                make = SuitePhoto
                extra = {"suite": suite}
            else:
                self.stderr.write(f"{group}: unknown group, skipped.")
                continue

            if existing.exists():
                if not replace:
                    self.stdout.write(f"{group}: already has photos, skipped.")
                    continue
                for photo in existing:
                    photo.image.delete(save=False)
                    photo.thumbnail.delete(save=False)
                existing.delete()

            with transaction.atomic():
                for order, item in enumerate(items, start=1):
                    path = source / group / item["file"]
                    with path.open("rb") as fh:
                        photo = make(
                            alt_ru=item.get("alt_ru", ""),
                            alt_en=item.get("alt_en", ""),
                            order=order,
                            **extra,
                        )
                        photo.image = File(fh, name=f"{group}-{item['file']}")
                        photo.save()
            self.stdout.write(self.style.SUCCESS(f"{group}: {len(items)} photos loaded."))
