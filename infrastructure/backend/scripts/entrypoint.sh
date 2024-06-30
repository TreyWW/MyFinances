#!/bin/sh

echo "BEFORE MIGRATE"
python3 manage.py migrate --no-input
echo "BEFORE COLLECT STATIC"
python3 manage.py collectstatic --no-input
echo "BEFORE RUN APP"
gunicorn settings.wsgi:application --bind 0.0.0.0:9012 --workers 2
