from django.test import TestCase, override_settings
from django.urls import reverse

from hotel.models import HotelInfo, Suite


class SeedDataTests(TestCase):
    def test_seven_suites_with_correct_capacity(self):
        capacities = dict(Suite.objects.values_list("number", "capacity"))
        self.assertEqual(capacities, {1: 4, 2: 2, 3: 3, 4: 2, 5: 2, 6: 2, 7: 2})


class OnePageTests(TestCase):
    def test_page_renders_in_both_languages(self):
        ru = self.client.get("/ru/")
        self.assertContains(ru, "Время только для вас")
        self.assertContains(ru, "Номера от двух часов")
        self.assertNotContains(ru, "Номера на час")
        en = self.client.get("/en/")
        self.assertContains(en, "Time just for you")
        self.assertContains(en, "Rooms from two hours")

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

    def test_suite_names_are_not_mentioned(self):
        response = self.client.get("/ru/")
        self.assertNotContains(response, "Люкс")

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
        self.assertNotContains(response, "за несколько минут")

    def test_no_messenger_block_when_none_are_set(self):
        info = HotelInfo.load()
        info.telegram = info.whatsapp = info.max_url = ""
        info.save()
        response = self.client.get("/ru/")
        self.assertNotContains(response, 'class="messengers"')

    def test_real_contacts_are_filled_in_by_migration(self):
        info = HotelInfo.load()
        self.assertEqual(info.phone, "+7 965 317-40-32")
        self.assertEqual(info.email, "pushkahotel@yandex.ru")
        response = self.client.get("/ru/")
        self.assertContains(response, 'href="tel:+79653174032"')
        self.assertContains(response, "mailto:pushkahotel@yandex.ru")

    def test_room_perks_are_listed(self):
        ru = self.client.get("/ru/")
        for text in ("В каждом номере", "Кондиционер", "Окна во внутренний двор", "Гигиенические наборы", "Тапочки"):
            self.assertContains(ru, text)
        en = self.client.get("/en/")
        self.assertContains(en, "Windows onto the courtyard")
        self.assertNotContains(ru, "Алкогол")
        self.assertContains(ru, "Как получить бутылку игристого в подарок?")
        self.assertContains(ru, "по воскресеньям — бесплатно")

    def test_boss_feedback_texts(self):
        ru = self.client.get("/ru/")
        for text in (
            "Почему пары выбирают «Пушку»",
            "Частые вопросы гостей",
            "Вывески у нас нет",
            "побыть вместе",
        ):
            self.assertContains(ru, text)
        for text in (
            "наедине",
            "никому не рассказываем",
            "Не хватает только вас",
            "Загляните ненадолго",
            "Возможна оплата наличными",
            "Номер вы выбираете сами",
            "Без доплат за гостей",
            "доплат за второго гостя",
        ):
            self.assertNotContains(ru, text)

    def test_hourly_setup_migration(self):
        hidden = set(Suite.objects.filter(is_active=False).values_list("number", flat=True))
        self.assertEqual(hidden, {1, 7})
        info = HotelInfo.load()
        response = self.client.get("/ru/")
        self.assertContains(response, "Большой Путинковский переулок, 5, Москва")
        self.assertContains(response, "2 минуты пешком от метро «Пушкинская», «Тверская» и «Чеховская»")
        self.assertContains(response, 'href="https://wa.me/79653174032"')
        self.assertContains(response, 'href="https://t.me/+79653174032"')
        self.assertContains(response, 'href="https://max.ru/u/f9LHodD0cOLHhU72vBDy5Bp6WeHujlbYNGtDpc8FmKjgJLkQ11XJA7PH-6o"')
        self.assertContains(response, "yandex.ru/maps/?text=")
        self.assertContains(response, 'class="map"')
        self.assertContains(response, "hotel/img/map.jpg")
        self.assertNotContains(response, "<iframe")
        en = self.client.get("/en/")
        self.assertContains(en, "5 Bolshoy Putinkovsky Lane, Moscow")

    def test_telegram_username_still_works(self):
        info = HotelInfo.load()
        info.telegram = "@pushka_hotel"
        self.assertEqual(info.telegram_url, "https://t.me/pushka_hotel")

    def test_rates_block(self):
        ru = self.client.get("/ru/")
        for text in ("Тариф «Свидание»", "Тариф «Наслаждение»", "3\u00a0500\u00a0₽", "4\u00a0000\u00a0₽", 'href="#tariffs"'):
            self.assertContains(ru, text)
        # The extension price is said once, under the rates, not in the promo cards.
        self.assertContains(ru, "Продление каждого следующего часа", count=1)
        en = self.client.get("/en/")
        self.assertContains(en, "The “Pleasure” rate")

    def test_new_logo(self):
        ru = self.client.get("/ru/")
        self.assertContains(ru, "logo-light.svg")


@override_settings(
    ALLOWED_HOSTS=["pushka-hotel.ru", "www.pushka-hotel.ru", "pushka-hotel.online"],
    PRIMARY_HOST="pushka-hotel.ru",
)
class PrimaryHostTests(TestCase):
    def test_extra_domain_redirects_to_main_one(self):
        response = self.client.get("/en/?x=1", HTTP_HOST="pushka-hotel.online")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "http://pushka-hotel.ru/en/?x=1")

    def test_main_domain_and_www_are_served(self):
        self.assertEqual(self.client.get("/ru/", HTTP_HOST="pushka-hotel.ru").status_code, 200)
        self.assertEqual(self.client.get("/ru/", HTTP_HOST="www.pushka-hotel.ru").status_code, 200)
