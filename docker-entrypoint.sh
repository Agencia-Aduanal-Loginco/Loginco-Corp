#!/bin/sh
set -e

python manage.py migrate --noinput --settings=config.settings.production
python manage.py createcachetable --settings=config.settings.production
python manage.py collectstatic --noinput --settings=config.settings.production

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
