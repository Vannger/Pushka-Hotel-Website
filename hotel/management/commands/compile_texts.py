"""Turn the edited translation file into the one the site reads.

Does the same as Django's compilemessages, but needs no extra programs,
so it also works on Windows:

    python manage.py compile_texts
"""

from pathlib import Path

import polib
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Compile locale/*/LC_MESSAGES/django.po into django.mo."

    def handle(self, *args, **options):
        files = [p for folder in settings.LOCALE_PATHS for p in Path(folder).glob("*/LC_MESSAGES/django.po")]
        if not files:
            raise CommandError("No django.po files found.")
        for po_path in files:
            try:
                po = polib.pofile(str(po_path))
            except (OSError, ValueError) as error:
                raise CommandError("%s could not be read: %s" % (po_path, error))
            fuzzy = [entry.msgid for entry in po.fuzzy_entries()]
            po.save_as_mofile(str(po_path.with_suffix(".mo")))
            self.stdout.write(self.style.SUCCESS("Compiled %s (%d texts)." % (po_path, len(po.translated_entries()))))
            for msgid in fuzzy:
                self.stdout.write(self.style.WARNING("Not used until you delete its '#, fuzzy' line: %s" % msgid[:70]))
