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

### On Windows

The quickest way to look at the site is with SQLite, so PostgreSQL is not needed.

1. Install [Python](https://www.python.org/downloads/) 3.12 or newer and tick
   "Add python.exe to PATH" in the installer. Install [Git](https://git-scm.com/download/win).
2. Open PowerShell and run:

   ```powershell
   git clone https://github.com/Vannger/Pushka-Hotel-Website.git
   cd Pushka-Hotel-Website
   git checkout feature/hourly-one-page
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   copy .env.example .env
   notepad .env
   ```

   If PowerShell refuses to run `Activate.ps1`, run
   `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.
3. In Notepad, make the line `POSTGRES_DB=` empty, save and close.
4. Back in PowerShell:

   ```powershell
   python manage.py migrate
   python manage.py load_photos
   python manage.py createsuperuser
   python manage.py runserver
   ```

5. Open http://127.0.0.1:8000/ for the site and http://127.0.0.1:8000/ru/admin/ for
   the admin panel. Press Ctrl+C in PowerShell to stop the server.

Next time, only these are needed:

```powershell
cd Pushka-Hotel-Website
.venv\Scripts\Activate.ps1
git pull
python manage.py migrate
python manage.py runserver
```

### In VS Code

Do the first-time setup above once (steps 1 to 4, but you can skip `runserver`).
Then:

1. Install the **Python** extension by Microsoft (Ctrl+Shift+X, search "Python").
2. File → Open Folder… and choose the `Pushka-Hotel-Website` folder.
3. Press Ctrl+Shift+P, run **Python: Select Interpreter** and pick the one marked
   `.venv`. VS Code remembers this.
4. Press F5 and choose **Run the site**. Open http://127.0.0.1:8000/.
   Shift+F5 stops it. After `git pull`, run **Update the database (migrate)** the
   same way before running the site.

The built-in terminal (Ctrl+`) activates `.venv` by itself, so any
`python manage.py ...` command from above works there too.

### Changing the texts yourself

Every text on the page lives in one file: `locale/ru/LC_MESSAGES/django.po`.
Each text has two lines there:

```
msgid "Time just for you"
msgstr "Время только для вас"
```

- `msgstr` is the Russian text on the site. Change only the part inside the quotes.
- `msgid` is the English text and also the text's name. Do not touch it here,
  or the Russian text stops showing.
- Keep the quotes. If the text itself needs quotation marks, use «ёлочки»,
  or write `\"` for straight ones.
- A long text can be split over several lines, each in its own quotes. They are
  joined together.
- If a text has a `#, fuzzy` line above it, the site ignores it. Delete that line
  once the text is right.

To find a text, press Ctrl+Shift+F in VS Code and search for a few words of
it in Russian. After saving, press F5 → **Run the site**: VS Code compiles the
texts first. From a terminal, run `python manage.py compile_texts`, then
restart the server.

To change an English text, change the same English sentence in **both**
`hotel/templates/hotel/home.html` and in its `msgid` in `django.po`, so they
stay identical, then compile again.

Phone, email, address, directions and messengers are not in this file.
Change them in the admin panel under **Информация об отеле** (hotel information).

### One file for someone without the server

`python manage.py export_html` saves the Russian page as `pushka-hotel.html`, with
the styles, fonts and photos built in. It opens with a double-click in any browser.
Only the messenger links and the Yandex Maps link need the internet, and there is no language
switch. Add `--lang en` for the English page. Run it again after changing photos or
contacts, because the file is a copy and does not update itself.

To create the PostgreSQL database:

```sql
CREATE USER pushka WITH PASSWORD 'pushka';
CREATE DATABASE pushka OWNER pushka;
```

If `POSTGRES_DB` is empty in `.env`, a local SQLite file is used instead.

## Putting the site on Reg.ru

The site runs on Reg.ru shared hosting with the **ispmanager** panel, through
`deploy/regru.sh`. It uses SQLite there, so no database needs to be ordered.

In the Reg.ru panel, once:

1. Attach the domain to the hosting and add it under **Сайты**.
2. **Сайты** → the domain → **Изменить**: turn on **CGI-скрипты** and **Python**,
   pick the newest Python 3 (3.10 or newer) and save.
3. Turn on SSH access for the hosting and note the login, server and password.
4. Order the free SSL certificate for the domain. The admin login only works over https.

Then over SSH (in PowerShell: `ssh <login>@<server>`):

```bash
git clone https://github.com/Vannger/Pushka-Hotel-Website.git pushka-hotel-website
bash pushka-hotel-website/deploy/regru.sh <domain>
cd ~/pushka-hotel-website && ~/pushka-venv/bin/python manage.py createsuperuser
```

To open the same site on a second domain, add it in the panel as an alias
(**Сайты** → the domain → **Изменить** → «Псевдонимы») and list it after the main
domain: `bash deploy/regru.sh pushka-hotel.ru pushka-hotel.online`.

The script prints the Python version it used. The site's Python in the panel must be
the same. To update the site later:

```bash
cd ~/pushka-hotel-website && git pull && bash deploy/regru.sh <domain>
```

The code, `.env` and the database stay in `~/pushka-hotel-website`, outside the web
folder. Only `passenger_wsgi.py`, `static/` and `media/` go into `~/www/<domain>/`.

## Where things live

| What | Where |
|---|---|
| Address, how to find us, phone, Telegram, WhatsApp, MAX, email | Admin panel → Hotel information |
| Map picture (from the hotel's business card) | `hotel/static/hotel/img/map.jpg` |
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

- The phone, email, address, directions and messenger links are filled in by
  migrations `0005` to `0008`, and can be changed in admin panel → Hotel information.
- Suites 1 and 7 are hidden because they are not let by the hour.
  Messenger buttons appear only for the messengers that are filled in.
- The promo texts only promise what the hotel confirmed for every room: quiet, windows
  onto the courtyard, air conditioning, and complimentary chocolates, water and tea.
- Alcoholic drinks are mentioned in one plain line only, because Russian law bans
  alcohol advertising online (38-FZ, art. 21). Keep it that way, and keep alcohol
  off the banners.

## Tests

```bash
python manage.py test hotel
```
