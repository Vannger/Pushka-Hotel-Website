"""Set up the hotel for hourly guests.

Suites 1 and 7 are not let by the hour, so they are hidden. The address,
directions, map and messenger contacts are filled in.
"""

from django.db import migrations

ADDRESS_RU = "Большой Путинковский переулок, 5, Москва"
ADDRESS_EN = "5 Bolshoy Putinkovsky Lane, Moscow"
DIRECTIONS_RU = "2 минуты пешком от метро «Чеховская», 4 минуты от «Пушкинской» и «Тверской»"
DIRECTIONS_EN = "2 minutes on foot from Chekhovskaya metro, 4 minutes from Pushkinskaya and Tverskaya"
MAP_URL = "https://yandex.ru/map-widget/v1/?mode=search&z=17&text=Москва,+Большой+Путинковский+переулок,+5"
PHONE = "+7 965 317-40-32"
NOT_HOURLY = (1, 7)


def forwards(apps, schema_editor):
    Suite = apps.get_model("hotel", "Suite")
    Suite.objects.filter(number__in=NOT_HOURLY).update(is_active=False)

    HotelInfo = apps.get_model("hotel", "HotelInfo")
    info, _created = HotelInfo.objects.get_or_create(pk=1)
    info.address_ru = ADDRESS_RU
    info.address_en = ADDRESS_EN
    info.directions_ru = DIRECTIONS_RU
    info.directions_en = DIRECTIONS_EN
    info.map_embed_url = MAP_URL
    # WhatsApp and Telegram find the hotel by its phone number.
    info.whatsapp = PHONE
    info.telegram = PHONE
    info.save()


def backwards(apps, schema_editor):
    Suite = apps.get_model("hotel", "Suite")
    Suite.objects.filter(number__in=NOT_HOURLY).update(is_active=True)


class Migration(migrations.Migration):
    dependencies = [("hotel", "0005_real_contacts")]

    operations = [migrations.RunPython(forwards, backwards)]
