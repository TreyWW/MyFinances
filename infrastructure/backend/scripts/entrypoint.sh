#!/bin/sh

echo "[SYSTEM] [DJANGO] About to migrate"
python3 manage.py migrate --no-input

echo "[SYSTEM] [DJANGO] About to collect static"
python3 manage.py collectstatic --no-input

# Start Gunicorn in the background
echo "[SYSTEM] [DJANGO] Starting Gunicorn"
gunicorn settings.wsgi:application --bind 0.0.0.0:9012 --workers 2 &

# Start Celery in the background
#echo "[SYSTEM] [CELERY] Starting Celery"
#celery -A backend worker --loglevel=info &

# Wait for background processes to finish
wait -n
