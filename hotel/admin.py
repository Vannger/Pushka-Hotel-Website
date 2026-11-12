from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import WEEKDAY_PRICE_FIELDS, HotelInfo, HotelPhoto, Suite, SuitePhoto

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
    # The list doubles as a price table: every weekday price can be edited
    # right in the list and saved with one button.
    list_display = ("number", "name_ru", *WEEKDAY_PRICE_FIELDS)
    list_display_links = ("number", "name_ru")
    list_editable = WEEKDAY_PRICE_FIELDS
    prepopulated_fields = {"slug": ("name_en",)}
    inlines = [SuitePhotoInline]
    fieldsets = (
        (None, {"fields": ("number", "slug", "capacity", "area_m2", "is_active")}),
        (
            _("Price per night by day of the week, ₽"),
            {
                "fields": (WEEKDAY_PRICE_FIELDS,),
                "classes": ("price-days",),
                "description": _(
                    "Each price is for the night that starts on that day. "
                    "For example, Friday is the night from Friday to Saturday."
                ),
            },
        ),
        (_("Russian"), {"fields": ("name_ru", "summary_ru", "description_ru", "amenities_ru")}),
        (_("English"), {"fields": ("name_en", "summary_en", "description_en", "amenities_en")}),
    )

    class Media:
        css = {"all": ("hotel/admin.css",)}


@admin.register(HotelPhoto)
class HotelPhotoAdmin(admin.ModelAdmin):
    list_display = (preview, "alt_ru", "order")
    list_display_links = (preview, "alt_ru")
    list_editable = ("order",)
    fields = (preview, "image", "alt_ru", "alt_en", "order")
    readonly_fields = (preview,)


@admin.register(HotelInfo)
class HotelInfoAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not HotelInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
