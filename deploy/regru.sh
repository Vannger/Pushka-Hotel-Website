#!/usr/bin/env bash
# Puts the site on Reg.ru shared hosting (ispmanager panel), or updates it.
#
# Run it over SSH from your home folder:
#     bash pushka-hotel-website/deploy/regru.sh pushkahotel.com
#
# Run it again after every `git pull` to update the site. It is safe to repeat:
# it keeps the database, the .env file and the photos already on the site.
#
# Layout it creates (nothing secret lives inside the web folder):
#     ~/pushka-hotel-website      the code, .env and the SQLite database
#     ~/pushka-venv               Python packages
#     ~/www/<domain>/             web folder: passenger_wsgi.py, static/, media/
set -euo pipefail

DOMAIN="${1:-}"
if [ -z "$DOMAIN" ]; then
  echo "Usage: bash deploy/regru.sh <domain>    for example: bash deploy/regru.sh pushkahotel.com" >&2
  exit 1
fi

APP="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$HOME/pushka-venv"
SITE="$HOME/www/$DOMAIN"

if [ ! -d "$SITE" ]; then
  echo "Folder $SITE does not exist. Add the site for $DOMAIN in the panel first (Sites)." >&2
  exit 1
fi

# 1. Python: PYTHON=/opt/python/python-3.x.y/bin/python picks one by hand,
#    otherwise the newest 3.10+ on the server is used.
if [ -z "${PYTHON:-}" ]; then
  PYTHON="$(ls -d /opt/python/python-3.*/bin/python 2>/dev/null | sort -V | tail -n 1 || true)"
fi
if [ -z "$PYTHON" ] || ! "$PYTHON" -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
  echo "Django 5.2 needs Python 3.10 or newer. Found: ${PYTHON:-none}." >&2
  echo "Available: $(ls -d /opt/python/python-3.*/bin/python 2>/dev/null | tr '\n' ' ')" >&2
  exit 1
fi
PYVER="$("$PYTHON" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
echo "== Using $PYTHON (Python $PYVER)"

# 2. Packages
if [ ! -x "$VENV/bin/python" ] || ! "$VENV/bin/python" -c "import sys; sys.exit(not sys.version.startswith('$PYVER'))"; then
  rm -rf "$VENV"
  "$PYTHON" -m venv "$VENV"
fi
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet -r "$APP/requirements.txt"
if ! "$VENV/bin/python" -c 'import sqlite3, sys; sys.exit(sqlite3.sqlite_version_info < (3, 31))'; then
  echo "== The server's SQLite is too old for Django, installing a newer one"
  "$VENV/bin/pip" install --quiet pysqlite3-binary
fi

# 3. Settings, written once. Edit ~/pushka-hotel-website/.env later if needed.
if [ ! -f "$APP/.env" ]; then
  SECRET="$("$VENV/bin/python" -c 'import secrets; print(secrets.token_urlsafe(50))')"
  cat > "$APP/.env" <<ENV
DJANGO_SECRET_KEY=$SECRET
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
DJANGO_CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
POSTGRES_DB=
DJANGO_SQLITE_PATH=$APP/db.sqlite3
DJANGO_STATIC_ROOT=$SITE/static
DJANGO_MEDIA_ROOT=$SITE/media
ENV
  chmod 600 "$APP/.env"
  echo "== Wrote $APP/.env"
fi

# 4. Database, styles and photos
cd "$APP"
"$VENV/bin/python" manage.py migrate --noinput
"$VENV/bin/python" manage.py collectstatic --noinput --clear --verbosity 0
"$VENV/bin/python" manage.py load_photos

# 5. The file the web server starts the site from
cat > "$SITE/passenger_wsgi.py" <<WSGI
# Written by deploy/regru.sh. Starts the Pushka Hotel site.
import os
import sys

sys.path.insert(0, "$APP")
sys.path.insert(1, "$VENV/lib/python$PYVER/site-packages")
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
WSGI

# The hosting's placeholder page would hide the site.
for page in index.html index.php; do
  if [ -f "$SITE/$page" ]; then
    mv "$SITE/$page" "$SITE/$page.old"
    echo "== Renamed the placeholder $page to $page.old"
  fi
done

touch "$SITE/.restart-app"
echo
echo "Done. In the panel, the site $DOMAIN must use Python $PYVER (Sites → $DOMAIN → Edit)."
echo "Open https://$DOMAIN/ in a minute. First time only: create the admin login with"
echo "    cd ~/pushka-hotel-website && ~/pushka-venv/bin/python manage.py createsuperuser"
