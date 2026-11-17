"""The hotel's MAX invite link, so the MAX button appears next to the others."""

from django.db import migrations

MAX_URL = "https://max.ru/u/f9LHodD0cOLHhU72vBDy5Bp6WeHujlbYNGtDpc8FmKjgJLkQ11XJA7PH-6o"


def forwards(apps, schema_editor):
    HotelInfo = apps.get_model("hotel", "HotelInfo")
    HotelInfo.objects.filter(pk=1).update(max_url=MAX_URL)


class Migration(migrations.Migration):
    dependencies = [("hotel", "0007_metro_two_minutes")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
