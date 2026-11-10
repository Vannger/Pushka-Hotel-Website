from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import HotelInfo, Suite, SuitePhoto

admin.site.site_header = _("Pushka Hotel administration")
admin.site.site_title = _("Pushka Hotel")


class SuitePhotoInline(admin.TabularInline):
    model = SuitePhoto
    extra = 1


@admin.register(Suite)
class SuiteAdmin(admin.ModelAdmin):
    list_display = ("number", "name_ru", "capacity", "price_per_night", "is_active")
    list_editable = ("price_per_night", "is_active")
    prepopulated_fields = {"slug": ("name_en",)}
    inlines = [SuitePhotoInline]
    fieldsets = (
        (None, {"fields": ("number", "slug", "capacity", "area_m2", "price_per_night", "is_active")}),
        (_("Russian"), {"fields": ("name_ru", "summary_ru", "description_ru", "amenities_ru")}),
        (_("English"), {"fields": ("name_en", "summary_en", "description_en", "amenities_en")}),
    )


@admin.register(HotelInfo)
class HotelInfoAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not HotelInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
