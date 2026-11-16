from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import WEEKDAY_PRICE_FIELDS, HotelInfo, Suite, SuitePhoto

admin.site.site_header = _("Pushka Hotel administration")
admin.site.site_title = _("Pushka Hotel")


@admin.display(description=_("preview"))
def preview(obj):
    if not obj.pk or not obj.image:
        return "—"
    return format_html('<img src="{}" alt="" style="height:72px;border-radius:4px">', obj.thumb_url)


class SuitePhotoInline(admin.TabularInline):
    model = SuitePhoto
    extra = 1
    fields = (preview, "image", "alt_ru", "alt_en", "order")
    readonly_fields = (preview,)


@admin.register(Suite)
class SuiteAdmin(admin.ModelAdmin):
    # The site is a single page that shows the photos of all suites mixed
    # together, so a suite is mostly a folder of photos here.
    list_display = ("number", "name_ru", "photo_count", "is_active")
    list_display_links = ("number", "name_ru")
    list_editable = ("is_active",)
    prepopulated_fields = {"slug": ("name_en",)}
    inlines = [SuitePhotoInline]
    fieldsets = (
        (None, {"fields": ("number", "name_ru", "is_active")}),
        (
            _("Not shown on the site"),
            {
                "classes": ("collapse", "price-days"),
                "description": _(
                    "The site does not show suite names, descriptions or prices. "
                    "These fields are kept in case separate suite pages are needed again."
                ),
                "fields": (
                    "slug",
                    "name_en",
                    "capacity",
                    "area_m2",
                    WEEKDAY_PRICE_FIELDS,
                    "summary_ru",
                    "summary_en",
                    "description_ru",
                    "description_en",
                    "amenities_ru",
                    "amenities_en",
                ),
            },
        ),
    )

    class Media:
        css = {"all": ("hotel/admin.css",)}

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(photo_count=Count("photos"))

    @admin.display(description=_("photos"), ordering="photo_count")
    def photo_count(self, obj):
        return obj.photo_count


@admin.register(HotelInfo)
class HotelInfoAdmin(admin.ModelAdmin):
    # Check-in and check-out times are not shown on the one-page site.
    fields = ("name_ru", "name_en", "address_ru", "address_en", "phone", "email", "map_embed_url")

    def has_add_permission(self, request):
        return not HotelInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
