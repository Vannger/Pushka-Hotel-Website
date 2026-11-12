from datetime import timedelta

from django.db import models
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from . import images

# One price field per day of the week, in date.weekday() order (Monday = 0).
WEEKDAY_PRICE_FIELDS = (
    "price_mon",
    "price_tue",
    "price_wed",
    "price_thu",
    "price_fri",
    "price_sat",
    "price_sun",
)
WEEKDAY_NAMES = (
    _("Monday"),
    _("Tuesday"),
    _("Wednesday"),
    _("Thursday"),
    _("Friday"),
    _("Saturday"),
    _("Sunday"),
)


class TranslatedFieldsMixin:
    """Return the `<field>_ru` or `<field>_en` value for the active language."""

    def tr(self, field):
        lang = (get_language() or "ru")[:2]
        value = getattr(self, f"{field}_{lang}", "")
        # Fall back to Russian if the English text has not been written yet.
        return value or getattr(self, f"{field}_ru", "")


class HotelInfo(TranslatedFieldsMixin, models.Model):
    """Contact details shown across the site. Only one row is ever used."""

    name_ru = models.CharField(_("name (Russian)"), max_length=100, default="Отель «Пушка»")
    name_en = models.CharField(_("name (English)"), max_length=100, default="Pushka Hotel")
    address_ru = models.CharField(_("address (Russian)"), max_length=255, blank=True)
    address_en = models.CharField(_("address (English)"), max_length=255, blank=True)
    phone = models.CharField(_("phone"), max_length=50, blank=True)
    email = models.EmailField(_("email"), blank=True)
    check_in_time = models.TimeField(_("check-in time"), default="14:00")
    check_out_time = models.TimeField(_("check-out time"), default="12:00")
    map_embed_url = models.URLField(
        _("map embed URL"),
        blank=True,
        help_text=_("Yandex Maps constructor link for the contacts page (optional)."),
    )

    class Meta:
        verbose_name = _("hotel information")
        verbose_name_plural = _("hotel information")

    def __str__(self):
        return self.name_ru

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def name(self):
        return self.tr("name")

    @property
    def address(self):
        return self.tr("address")


def _price_field(label):
    return models.PositiveIntegerField(label)


class Suite(TranslatedFieldsMixin, models.Model):
    number = models.PositiveSmallIntegerField(_("suite number"), unique=True)
    slug = models.SlugField(_("URL name"), unique=True)
    name_ru = models.CharField(_("name (Russian)"), max_length=100)
    name_en = models.CharField(_("name (English)"), max_length=100, blank=True)
    summary_ru = models.CharField(_("short description (Russian)"), max_length=255, blank=True)
    summary_en = models.CharField(_("short description (English)"), max_length=255, blank=True)
    description_ru = models.TextField(_("description (Russian)"), blank=True)
    description_en = models.TextField(_("description (English)"), blank=True)
    amenities_ru = models.TextField(
        _("amenities (Russian)"), blank=True, help_text=_("One item per line.")
    )
    amenities_en = models.TextField(
        _("amenities (English)"), blank=True, help_text=_("One item per line.")
    )
    capacity = models.PositiveSmallIntegerField(_("maximum guests"))
    area_m2 = models.PositiveSmallIntegerField(_("area, m²"), null=True, blank=True)
    # The price of a night belongs to the day the night starts on:
    # price_fri is the night from Friday to Saturday.
    price_mon = _price_field(_("Mon"))
    price_tue = _price_field(_("Tue"))
    price_wed = _price_field(_("Wed"))
    price_thu = _price_field(_("Thu"))
    price_fri = _price_field(_("Fri"))
    price_sat = _price_field(_("Sat"))
    price_sun = _price_field(_("Sun"))
    is_active = models.BooleanField(_("shown on the site"), default=True)

    class Meta:
        ordering = ["number"]
        verbose_name = _("suite")
        verbose_name_plural = _("suites")

    def __str__(self):
        return f"{self.number}. {self.name_ru}"

    def get_absolute_url(self):
        return reverse("hotel:suite_detail", kwargs={"slug": self.slug})

    @property
    def name(self):
        return self.tr("name")

    @property
    def summary(self):
        return self.tr("summary")

    @property
    def description(self):
        return self.tr("description")

    @property
    def amenities(self):
        return [line.strip() for line in self.tr("amenities").splitlines() if line.strip()]

    @property
    def cover(self):
        photos = self.photos.all()
        return photos[0] if photos else None

    # Prices -----------------------------------------------------------

    @property
    def weekday_prices(self):
        """[(day name, price), ...] from Monday to Sunday."""
        return [
            (name, getattr(self, field))
            for name, field in zip(WEEKDAY_NAMES, WEEKDAY_PRICE_FIELDS)
        ]

    @property
    def min_price(self):
        return min(getattr(self, field) for field in WEEKDAY_PRICE_FIELDS)

    @property
    def has_single_price(self):
        return len({getattr(self, field) for field in WEEKDAY_PRICE_FIELDS}) == 1

    def price_for_night(self, day):
        """Price of the night that starts on `day` (a date)."""
        return getattr(self, WEEKDAY_PRICE_FIELDS[day.weekday()])

    def price_for_stay(self, check_in, check_out):
        """Total for all nights from check-in up to (not including) check-out."""
        nights = (check_out - check_in).days
        return sum(self.price_for_night(check_in + timedelta(days=i)) for i in range(nights))


def photo_upload_to(instance, filename):
    return f"{instance.upload_folder}/{filename}"


def thumbnail_upload_to(instance, filename):
    return f"{instance.upload_folder}/thumbs/{filename}"


class Photo(TranslatedFieldsMixin, models.Model):
    """A web-ready photo with a smaller copy for cards and thumbnails."""

    upload_folder = "photos"

    image = models.ImageField(_("photo"), upload_to=photo_upload_to)
    thumbnail = models.ImageField(
        _("thumbnail"), upload_to=thumbnail_upload_to, editable=False, blank=True
    )
    alt_ru = models.CharField(_("caption (Russian)"), max_length=150, blank=True)
    alt_en = models.CharField(_("caption (English)"), max_length=150, blank=True)
    order = models.PositiveSmallIntegerField(_("order"), default=0)

    class Meta:
        abstract = True
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):
        if self.image and not self.image._committed:
            # A new file was uploaded: resize it and make the thumbnail.
            self.image.seek(0)
            main, thumb = images.prepare(self.image.read())
            self.image.seek(0)
            if main is not None:
                self.image.save(images.jpeg_name(self.image.name), main, save=False)
            self.thumbnail.save(images.jpeg_name(self.image.name, "-thumb"), thumb, save=False)
        elif self.image and not self.thumbnail:
            with self.image.open("rb") as fh:
                _main, thumb = images.prepare(fh.read())
            self.thumbnail.save(images.jpeg_name(self.image.name, "-thumb"), thumb, save=False)
        super().save(*args, **kwargs)

    @property
    def thumb_url(self):
        return (self.thumbnail or self.image).url


class SuitePhoto(Photo):
    upload_folder = "suites"

    suite = models.ForeignKey(
        Suite, on_delete=models.CASCADE, related_name="photos", verbose_name=_("suite")
    )

    class Meta(Photo.Meta):
        verbose_name = _("photo")
        verbose_name_plural = _("photos")

    def __str__(self):
        return f"{self.suite} #{self.order}"

    @property
    def alt(self):
        return self.tr("alt") or self.suite.name


class HotelPhoto(Photo):
    """Photos of the hotel itself (corridors, kitchenette) for the About page."""

    upload_folder = "hotel"

    class Meta(Photo.Meta):
        verbose_name = _("hotel photo")
        verbose_name_plural = _("hotel photos")

    def __str__(self):
        return self.alt_ru or f"#{self.pk}"

    @property
    def alt(self):
        return self.tr("alt")
