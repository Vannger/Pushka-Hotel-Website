"""The hotel is 2 minutes on foot from all three metro stations."""

from django.db import migrations

DIRECTIONS_RU = "2 минуты пешком от метро «Пушкинская», «Тверская» и «Чеховская»"
DIRECTIONS_EN = "2 minutes on foot from Pushkinskaya, Tverskaya and Chekhovskaya metro stations"


def forwards(apps, schema_editor):
    HotelInfo = apps.get_model("hotel", "HotelInfo")
    HotelInfo.objects.filter(pk=1).update(directions_ru=DIRECTIONS_RU, directions_en=DIRECTIONS_EN)


class Migration(migrations.Migration):
    dependencies = [("hotel", "0006_hourly_setup")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
