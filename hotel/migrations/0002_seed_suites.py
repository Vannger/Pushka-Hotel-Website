"""Create the seven Pushka Hotel suites and the hotel contact record.

Prices are placeholders; change them in the admin panel.
"""

from decimal import Decimal

from django.db import migrations

TWO_GUESTS_RU = (
    "Уютный номер для двоих: двуспальная кровать, рабочее место и собственная ванная комната."
)
TWO_GUESTS_EN = (
    "A cosy suite for two with a double bed, a work desk and a private bathroom."
)

SUITES = [
    {
        "number": 1,
        "capacity": 4,
        "price": "8000",
        "name_ru": "Семейный люкс №1",
        "name_en": "Family Suite No. 1",
        "summary_ru": "Самый просторный номер отеля — для семьи или компании до четырёх человек.",
        "summary_en": "Our most spacious suite, for a family or a group of up to four.",
    },
    {
        "number": 3,
        "capacity": 3,
        "price": "6500",
        "name_ru": "Люкс №3 для троих",
        "name_en": "Suite No. 3 for Three",
        "summary_ru": "Номер для трёх гостей: двуспальная кровать и дополнительное спальное место.",
        "summary_en": "A suite for three guests with a double bed and an extra bed.",
    },
]
for number in (2, 4, 5, 6, 7):
    SUITES.append(
        {
            "number": number,
            "capacity": 2,
            "price": "5000",
            "name_ru": f"Люкс №{number}",
            "name_en": f"Suite No. {number}",
            "summary_ru": TWO_GUESTS_RU,
            "summary_en": TWO_GUESTS_EN,
        }
    )

AMENITIES_RU = "Бесплатный Wi-Fi\nСобственная ванная комната\nТелевизор\nЧайник и чайный набор\nПолотенца и халаты"
AMENITIES_EN = "Free Wi-Fi\nPrivate bathroom\nTV\nKettle and tea set\nTowels and bathrobes"


def seed(apps, schema_editor):
    Suite = apps.get_model("hotel", "Suite")
    HotelInfo = apps.get_model("hotel", "HotelInfo")

    for data in SUITES:
        Suite.objects.update_or_create(
            number=data["number"],
            defaults={
                "slug": f"suite-{data['number']}",
                "capacity": data["capacity"],
                "price_per_night": Decimal(data["price"]),
                "name_ru": data["name_ru"],
                "name_en": data["name_en"],
                "summary_ru": data["summary_ru"],
                "summary_en": data["summary_en"],
                "description_ru": data["summary_ru"],
                "description_en": data["summary_en"],
                "amenities_ru": AMENITIES_RU,
                "amenities_en": AMENITIES_EN,
            },
        )

    HotelInfo.objects.get_or_create(
        pk=1,
        defaults={
            "address_ru": "Адрес будет добавлен",
            "address_en": "Address to be added",
            "phone": "+7 (000) 000-00-00",
            "email": "info@example.com",
        },
    )


def unseed(apps, schema_editor):
    apps.get_model("hotel", "Suite").objects.filter(number__in=[s["number"] for s in SUITES]).delete()


class Migration(migrations.Migration):
    dependencies = [("hotel", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]
