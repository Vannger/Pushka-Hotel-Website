from django.db import models
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _


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
    price_per_night = models.DecimalField(
        _("price per night, ₽"), max_digits=9, decimal_places=2
    )
    is_active = models.BooleanField(
        _("shown on the site"), default=True
    )

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
        return self.photos.first()


class SuitePhoto(TranslatedFieldsMixin, models.Model):
    suite = models.ForeignKey(
        Suite, on_delete=models.CASCADE, related_name="photos", verbose_name=_("suite")
    )
    image = models.ImageField(_("photo"), upload_to="suites/")
    alt_ru = models.CharField(_("caption (Russian)"), max_length=150, blank=True)
    alt_en = models.CharField(_("caption (English)"), max_length=150, blank=True)
    order = models.PositiveSmallIntegerField(_("order"), default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("photo")
        verbose_name_plural = _("photos")

    def __str__(self):
        return f"{self.suite} #{self.order}"

    @property
    def alt(self):
        return self.tr("alt") or self.suite.name
