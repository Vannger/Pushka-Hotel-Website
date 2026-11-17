"""Fill in the hotel's real phone and email."""

from django.db import migrations

PHONE = "+7 965 317-40-32"
EMAIL = "pushkahotel@yandex.ru"


def set_contacts(apps, schema_editor):
    HotelInfo = apps.get_model("hotel", "HotelInfo")
    info, _created = HotelInfo.objects.get_or_create(pk=1)
    info.phone = PHONE
    info.email = EMAIL
    info.save(update_fields=["phone", "email"])


class Migration(migrations.Migration):
    dependencies = [("hotel", "0004_contacts_messengers")]

    operations = [migrations.RunPython(set_contacts, migrations.RunPython.noop)]
