from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from hotel.models import Suite


class SeedDataTests(TestCase):
    def test_seven_suites_with_correct_capacity(self):
        capacities = dict(Suite.objects.values_list("number", "capacity"))
        self.assertEqual(capacities, {1: 4, 2: 2, 3: 3, 4: 2, 5: 2, 6: 2, 7: 2})


class PageTests(TestCase):
    pages = ["hotel:home", "hotel:suite_list", "hotel:about", "hotel:contacts"]

    def test_pages_render_in_both_languages(self):
        for lang in ("ru", "en"):
            with translation.override(lang):
                for name in self.pages:
                    url = reverse(name)
                    self.assertTrue(url.startswith(f"/{lang}/"))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, 200, url)

    def test_suite_detail_is_translated(self):
        suite = Suite.objects.get(number=1)
        with translation.override("ru"):
            response = self.client.get(suite.get_absolute_url())
        self.assertContains(response, "Семейный люкс №1")
        self.assertContains(response, "До 4 гостей")
        with translation.override("en"):
            response = self.client.get(suite.get_absolute_url())
        self.assertContains(response, "Family Suite No. 1")
        self.assertContains(response, "Up to 4 guests")

    def test_inactive_suite_is_hidden(self):
        suite = Suite.objects.get(number=2)
        suite.is_active = False
        suite.save()
        with translation.override("en"):
            self.assertEqual(self.client.get(suite.get_absolute_url()).status_code, 404)

    def test_root_redirects_to_language(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith("/ru/"))

    def test_language_switch_keeps_page(self):
        response = self.client.post(
            reverse("set_language"), {"language": "en", "next": "/ru/suites/"}
        )
        self.assertRedirects(response, "/en/suites/", fetch_redirect_response=False)
