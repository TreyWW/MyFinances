#!/bin/sh

python3 manage.py migrate backend --fake backend 0036_alter_client_address_clientdefaults

python3 manage.py migrate --no-input && python3 manage.py collectstatic --no-input

gunicorn settings.wsgi:application --bind 0.0.0.0:9012 --workers 2
