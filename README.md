# Pushka Hotel Website

One-page website for Pushka Hotel's guests who rent a room by the hour, in Russian
and English, built with Django and PostgreSQL.

The page has three things only:

- **Promo texts**: the headline and four short blocks.
- **Room photos**: the photos of all rooms mixed together, without names or numbers,
  because the hotel chooses the room for the guest.
- **Contacts**: address, phone, email and a map.

There are no suite pages, prices or booking. The earlier multi-page version with
them is in the history of the `feature/foundation` branch.

## Running locally

Requires Python 3.12+ and (optionally) PostgreSQL 14+.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then edit the values
python manage.py migrate           # also creates the seven suites
python manage.py load_photos       # adds the room photos from photos/
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ (redirects to `/ru/`) and the admin panel at `/ru/admin/`.

To create the PostgreSQL database:

```sql
CREATE USER pushka WITH PASSWORD 'pushka';
CREATE DATABASE pushka OWNER pushka;
```

If `POSTGRES_DB` is empty in `.env`, a local SQLite file is used instead.

## Where things live

| What | Where |
|---|---|
| Address, how to find us, phone, Telegram, WhatsApp, MAX, email, map link | Admin panel → Hotel information |
| Room photos | Admin panel → Suites → open a suite → Photos |
| Hiding all photos of one room | Admin panel → Suites: untick "shown on the site" |
| Original photos for the first load | `photos/` (one folder per suite, captions in `photos/photos.json`) |
| Promo texts and other page copy | `hotel/templates/hotel/home.html`, Russian translation in `locale/ru/LC_MESSAGES/django.po` |
| Styles, script, logo, fonts | `hotel/static/hotel/` |

Templates are written in English and translated to Russian through gettext.
After changing interface text:

```bash
python manage.py makemessages -l ru -l en   # updates the .po files (needs GNU gettext)
# edit locale/ru/LC_MESSAGES/django.po
python manage.py compilemessages
```

## Photos

The page deals the photos out like cards: the first photo of every suite, then the
second of every suite, and so on. Captions are used only as alternative text.
The photos of the hall (`photos/hotel/`) are loaded but not shown.

`python manage.py load_photos` loads `photos/` into the database and media folder.
It skips suites that already have photos; `--replace` reloads them.

Every photo uploaded in the admin panel is resized to at most 1920 px, turned the
right way up, stripped of camera metadata and given a thumbnail automatically.

The photos of suites 5 and 6 were taken on a phone, so they were enhanced with
Real-ESRGAN (`realesr-general-x4v3`, denoise strength 0.35) before being added.
The photos of suites 2–4 and the hall were already sharp, so they were only resized.

## What is kept but not shown

Suite names, descriptions, capacities and the prices for each day of the week stay
in the database, and `Suite.price_for_stay()` still works. The admin panel keeps
them in a collapsed block called "Not shown on the site". They are there in case
separate suite pages are needed again.

## Placeholders to replace

- Address, how to find us, messengers and map link: admin panel → Hotel information.
  The phone and email are filled in by migration `0005`.
  Messenger buttons appear only for the messengers that are filled in.
- Photos for suites 1 and 7.
- The promo texts only promise what the hotel confirmed for every room: quiet, windows
  onto the courtyard, air conditioning, and complimentary chocolates, water and tea.
- Alcoholic drinks are mentioned in one plain line only, because Russian law bans
  alcohol advertising online (38-FZ, art. 21). Keep it that way, and keep alcohol
  off the banners.

## Tests

```bash
python manage.py test hotel
```
