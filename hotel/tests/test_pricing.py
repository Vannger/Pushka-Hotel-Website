from datetime import date

from django.test import TestCase

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
