"""Give each suite its own price for every day of the week, and add hotel photos.

The single `price_per_night` is copied into all seven days, so nothing changes
for guests until the prices are edited in the admin panel.
"""

import hotel.models
from django.db import migrations, models

DAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
LABELS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def copy_price_to_days(apps, schema_editor):
    Suite = apps.get_model("hotel", "Suite")
    for suite in Suite.objects.all():
        for day in DAYS:
            setattr(suite, f"price_{day}", int(suite.price_per_night))
        suite.save()


def copy_monday_back(apps, schema_editor):
    Suite = apps.get_model("hotel", "Suite")
    Suite.objects.update(price_per_night=models.F("price_mon"))


class Migration(migrations.Migration):
    dependencies = [("hotel", "0002_seed_suites")]

    operations = [
        *[
            migrations.AddField(
                model_name="suite",
                name=f"price_{day}",
                field=models.PositiveIntegerField(default=0, verbose_name=label),
                preserve_default=False,
            )
            for day, label in zip(DAYS, LABELS)
        ],
        migrations.RunPython(copy_price_to_days, copy_monday_back),
        # A default keeps this step reversible; the field is removed right after.
        migrations.AlterField(
            model_name="suite",
            name="price_per_night",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=9, verbose_name="price per night, ₽"
            ),
        ),
        migrations.RemoveField(model_name="suite", name="price_per_night"),
        migrations.AlterField(
            model_name="suitephoto",
            name="image",
            field=models.ImageField(upload_to=hotel.models.photo_upload_to, verbose_name="photo"),
        ),
        migrations.AddField(
            model_name="suitephoto",
            name="thumbnail",
            field=models.ImageField(
                blank=True,
                editable=False,
                upload_to=hotel.models.thumbnail_upload_to,
                verbose_name="thumbnail",
            ),
        ),
        migrations.CreateModel(
            name="HotelPhoto",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "image",
                    models.ImageField(upload_to=hotel.models.photo_upload_to, verbose_name="photo"),
                ),
                (
                    "thumbnail",
                    models.ImageField(
                        blank=True,
                        editable=False,
                        upload_to=hotel.models.thumbnail_upload_to,
                        verbose_name="thumbnail",
                    ),
                ),
                ("alt_ru", models.CharField(blank=True, max_length=150, verbose_name="caption (Russian)")),
                ("alt_en", models.CharField(blank=True, max_length=150, verbose_name="caption (English)")),
                ("order", models.PositiveSmallIntegerField(default=0, verbose_name="order")),
            ],
            options={
                "verbose_name": "hotel photo",
                "verbose_name_plural": "hotel photos",
                "ordering": ["order", "id"],
                "abstract": False,
            },
            bases=(hotel.models.TranslatedFieldsMixin, models.Model),
        ),
    ]
