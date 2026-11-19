from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from hotel.models import HotelInfo, HotelPhoto, Suite


class AdminTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_superuser("boss", "boss@example.com", "pass"))

    def test_suite_list_shows_photo_counts_instead_of_prices(self):
        response = self.client.get(reverse("admin:hotel_suite_changelist"))
        self.assertContains(response, "field-photo_count", count=7)
        self.assertNotContains(response, "price_mon")

    def test_suite_can_be_hidden_from_the_list(self):
        suites = list(Suite.objects.order_by("number"))
        data = {
            "form-TOTAL_FORMS": str(len(suites)),
            "form-INITIAL_FORMS": str(len(suites)),
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "_save": "Save",
        }
        for i, suite in enumerate(suites):
            data[f"form-{i}-id"] = str(suite.pk)
            if suite.number != 7:
                data[f"form-{i}-is_active"] = "on"
        response = self.client.post(reverse("admin:hotel_suite_changelist"), data)
        self.assertEqual(response.status_code, 302)
        hidden = Suite.objects.filter(is_active=False).values_list("number", flat=True)
        self.assertEqual(list(hidden), [7])

    def test_suite_form_opens_and_has_no_link_to_a_suite_page(self):
        suite = Suite.objects.get(number=2)
        response = self.client.get(reverse("admin:hotel_suite_change", args=[suite.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "viewsitelink")

    def test_hotel_information_form_has_contacts_only(self):
        info = HotelInfo.load()
        response = self.client.get(reverse("admin:hotel_hotelinfo_change", args=[info.pk]))
        self.assertContains(response, 'name="phone"')
        self.assertNotContains(response, 'name="check_in_time"')

    def test_hotel_photos_are_not_offered(self):
        self.assertFalse(admin.site.is_registered(HotelPhoto))
