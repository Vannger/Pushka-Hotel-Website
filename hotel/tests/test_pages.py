from django.test import TestCase
from django.urls import reverse

from hotel.models import HotelInfo, Suite


class SeedDataTests(TestCase):
    def test_seven_suites_with_correct_capacity(self):
        capacities = dict(Suite.objects.values_list("number", "capacity"))
        self.assertEqual(capacities, {1: 4, 2: 2, 3: 3, 4: 2, 5: 2, 6: 2, 7: 2})


class OnePageTests(TestCase):
    def test_page_renders_in_both_languages(self):
        ru = self.client.get("/ru/")
        self.assertContains(ru, "Время только для двоих")
        self.assertContains(ru, "Номера на час")
        en = self.client.get("/en/")
        self.assertContains(en, "Time for just the two of you")
        self.assertContains(en, "Rooms by the hour")

    def test_root_redirects_to_language(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith("/ru/"))

    def test_language_switch_keeps_page(self):
        response = self.client.post(reverse("set_language"), {"language": "en", "next": "/ru/"})
        self.assertRedirects(response, "/en/", fetch_redirect_response=False)

    def test_there_are_no_other_pages(self):
        for path in ("/ru/suites/", "/ru/suites/suite-2/", "/ru/about/", "/ru/contacts/"):
            self.assertEqual(self.client.get(path).status_code, 404, path)

    def test_suites_and_prices_are_not_mentioned(self):
        response = self.client.get("/ru/")
        self.assertNotContains(response, "Люкс")
        self.assertNotContains(response, "₽")

    def test_contacts_are_shown(self):
        info = HotelInfo.load()
        info.address_ru = "Тверская ул., 1"
        info.phone = "+7 (900) 123-45-67"
        info.email = "hello@pushka.example"
        info.save()
        response = self.client.get("/ru/")
        self.assertContains(response, "Тверская ул., 1")
        self.assertContains(response, 'href="tel:+79001234567"')
        self.assertContains(response, "+7 (900) 123-45-67")
        self.assertContains(response, "mailto:hello@pushka.example")

    def test_no_call_buttons_without_a_phone(self):
        info = HotelInfo.load()
        info.phone = ""
        info.save()
        response = self.client.get("/ru/")
        self.assertNotContains(response, "tel:")
        self.assertNotContains(response, "call-bar")

    def test_messenger_buttons_and_directions(self):
        info = HotelInfo.load()
        info.address_ru = "Тверская ул., 1"
        info.directions_ru = "5 минут от метро «Пушкинская»"
        info.telegram = "@pushka_hotel"
        info.whatsapp = "+7 (900) 123-45-67"
        info.max_url = "https://max.ru/pushka"
        info.save()
        response = self.client.get("/ru/")
        self.assertContains(response, 'href="https://t.me/pushka_hotel"')
        self.assertContains(response, 'href="https://wa.me/79001234567"')
        self.assertContains(response, 'href="https://max.ru/pushka"')
        self.assertContains(response, "5 минут от метро «Пушкинская»")
        self.assertContains(response, "Отвечаем за несколько минут")

    def test_no_messenger_block_when_none_are_set(self):
        response = self.client.get("/ru/")
        self.assertNotContains(response, 'class="messengers"')
