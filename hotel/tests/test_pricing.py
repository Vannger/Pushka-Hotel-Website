from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from hotel.models import WEEKDAY_PRICE_FIELDS, Suite

# 2026-11-16 is a Monday.
MONDAY = date(2026, 11, 16)
PRICES = dict(zip(WEEKDAY_PRICE_FIELDS, [5000, 5000, 5000, 5500, 7000, 7500, 6000]))


class WeekdayPriceTests(TestCase):
    def setUp(self):
        self.suite = Suite.objects.get(number=2)
        for field, price in PRICES.items():
            setattr(self.suite, field, price)
        self.suite.save()

    def test_migration_copied_placeholder_price_to_every_day(self):
        suite = Suite.objects.get(number=1)
        self.assertEqual({getattr(suite, f) for f in WEEKDAY_PRICE_FIELDS}, {8000})
        self.assertTrue(suite.has_single_price)

    def test_price_for_night_uses_the_day_the_night_starts(self):
        self.assertEqual(self.suite.price_for_night(MONDAY), 5000)
        self.assertEqual(self.suite.price_for_night(date(2026, 11, 20)), 7000)  # Friday
        self.assertEqual(self.suite.price_for_night(date(2026, 11, 22)), 6000)  # Sunday

    def test_price_for_stay_adds_up_each_night(self):
        # Friday to Monday: Friday, Saturday and Sunday nights.
        total = self.suite.price_for_stay(date(2026, 11, 20), date(2026, 11, 23))
        self.assertEqual(total, 7000 + 7500 + 6000)
        # A full week costs the sum of all seven prices.
        self.assertEqual(self.suite.price_for_stay(MONDAY, date(2026, 11, 23)), sum(PRICES.values()))
        self.assertEqual(self.suite.price_for_stay(MONDAY, MONDAY), 0)

    def test_min_price(self):
        self.assertEqual(self.suite.min_price, 5000)
        self.assertFalse(self.suite.has_single_price)

    def test_suite_page_shows_price_for_each_day(self):
        with translation.override("ru"):
            response = self.client.get(self.suite.get_absolute_url())
        self.assertContains(response, "от 5\xa0000 ₽ за ночь")
        self.assertContains(response, "Пятница")
        self.assertContains(response, "7\xa0500 ₽")
        with translation.override("en"):
            response = self.client.get(self.suite.get_absolute_url())
        self.assertContains(response, "Saturday")

    def test_single_price_has_no_from_and_no_table(self):
        suite = Suite.objects.get(number=1)
        with translation.override("en"):
            response = self.client.get(suite.get_absolute_url())
        self.assertContains(response, "8,000 ₽ per night")
        self.assertNotContains(response, "price-table")


class PriceAdminTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User

        self.admin = User.objects.create_superuser("boss", "boss@example.com", "pass")
        self.client.force_login(self.admin)

    def test_prices_can_be_edited_in_the_suite_list(self):
        suites = list(Suite.objects.order_by("id"))
        data = {
            "form-TOTAL_FORMS": str(len(suites)),
            "form-INITIAL_FORMS": str(len(suites)),
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "_save": "Save",
        }
        for i, suite in enumerate(suites):
            data[f"form-{i}-id"] = str(suite.pk)
            for field in WEEKDAY_PRICE_FIELDS:
                data[f"form-{i}-{field}"] = str(getattr(suite, field))
        index = next(i for i, s in enumerate(suites) if s.number == 3)
        data[f"form-{index}-price_sat"] = "9900"
        with translation.override("ru"):
            response = self.client.post(reverse("admin:hotel_suite_changelist"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Suite.objects.get(number=3).price_sat, 9900)
        self.assertEqual(Suite.objects.get(number=3).price_fri, 6500)
