# Pushka Hotel Website

Bilingual (Russian / English) website for Pushka Hotel, built with Django and PostgreSQL.

## Roadmap

1. **Foundation and bilingual site**: pages, suites, admin panel, translations. *(this step)*
2. **Booking without payment**: availability calendar, booking requests, no double bookings, email notifications.
3. **Online payment**: YooKassa with 54-FZ receipts; the booking request form stays as a fallback.
4. **Launch**: Russian hosting, domain, HTTPS, privacy policy and personal data consent (152-FZ).

## Running locally

Requires Python 3.12+ and (optionally) PostgreSQL 14+.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then edit the values
python manage.py migrate           # also creates the seven suites
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
| Suites, photos, prices, hotel contacts | Admin panel (stored in the database) |
| Suite texts in both languages | `*_ru` / `*_en` fields on each suite |
| Interface texts (menus, buttons, page copy) | Templates in `hotel/templates/hotel/`, Russian translation in `locale/ru/LC_MESSAGES/django.po` |
| Styles and logo | `hotel/static/hotel/` |

Templates are written in English and translated to Russian through gettext.
After changing interface text:

```bash
python manage.py makemessages -l ru -l en   # updates the .po files (needs GNU gettext)
# edit locale/ru/LC_MESSAGES/django.po
python manage.py compilemessages
```

## Placeholders to replace

- Suite prices (8 000 / 6 500 / 5 000 ₽): edit in the admin panel.
- Address, phone, email and map link: admin panel → Hotel information.
- Suite photos: admin panel → Suites → open a suite → Photos.
- Suite descriptions and amenities are drafts and need checking against the real rooms.

## Tests

```bash
python manage.py test hotel
```
