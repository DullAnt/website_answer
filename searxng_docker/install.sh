#!/usr/bin/env bash
set -e

APP_ROOT=/usr/local/searxng
SRC_DIR=$APP_ROOT/searxng-src
VENV_DIR=$APP_ROOT/searx-pyenv
RUN_DIR=$APP_ROOT/run
LOG_DIR=$APP_ROOT/log

SETTINGS_DST=/etc/searxng/settings.yml
UWSGI_DST=/etc/uwsgi/apps-available/searxng.ini
NGINX_DST=/etc/nginx/default.apps-available/searxng.conf

echo "==> Creating user searxng"
sudo useradd -r -s /usr/sbin/nologin searxng 2>/dev/null || true

echo "==> Creating directories"
sudo mkdir -p "$APP_ROOT" "$RUN_DIR" "$LOG_DIR" /etc/searxng
sudo mkdir -p /etc/uwsgi/apps-available /etc/uwsgi/apps-enabled
sudo mkdir -p /etc/nginx/default.apps-available

echo "==> Copying source code"
sudo rm -rf "$SRC_DIR"
sudo cp -r ./searxng-src "$SRC_DIR"

if [ -x /usr/local/searxng/searx-pyenv/bin/python ]; then
  echo "==> Reusing existing local venv"
else
  echo "==> Existing venv not found, creating new one"
  sudo rm -rf "$VENV_DIR"
  sudo python3.11 -m venv "$VENV_DIR"
  sudo "$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel
  sudo "$VENV_DIR/bin/pip" install --no-index --find-links ./wheelhouse -r "$SRC_DIR/requirements.txt"
fi

echo "==> Installing configs"
sudo cp ./config/settings.yml "$SETTINGS_DST"
sudo cp ./config/searxng.ini "$UWSGI_DST"
sudo cp ./config/nginx-searxng.conf "$NGINX_DST"

echo "==> Enabling uwsgi app"
sudo ln -sf "$UWSGI_DST" /etc/uwsgi/apps-enabled/searxng.ini

echo "==> Fixing ownership"
sudo chown -R searxng:searxng "$APP_ROOT"
sudo chmod 755 "$APP_ROOT" "$RUN_DIR" "$LOG_DIR"

echo "==> Restarting services"
sudo systemctl restart uwsgi
sudo systemctl restart nginx

echo "==> Done"
echo "Check:"
echo "curl \"http://127.0.0.1/searxng/search?q=test&format=json\""