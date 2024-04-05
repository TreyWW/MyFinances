#!/bin/sh

python3 manage.py makemigrations --no-input && python3 manage.py migrate --no-input && python3 manage.py collectstatic --no-input
# compile translations
django-admin compilemessages --ignore=env

gunicorn settings.wsgi:application --bind 0.0.0.0:9012 --workers 2
