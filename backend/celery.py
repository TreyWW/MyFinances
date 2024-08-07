# backend/celery.py

from __future__ import absolute_import, unicode_literals
import os
import sys

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

CELERY_BROKER = os.environ.get("CELERY_BROKER") or os.environ.get("REDIS_CACHE_HOST") or "redis://localhost:6379/0"
CELERY_BACKEND = os.environ.get("CELERY_BACKEND") or os.environ.get("REDIS_CACHE_HOST") or "redis://localhost:6379/0"

app = Celery("backend", broker=CELERY_BROKER, backend=CELERY_BACKEND)

app.config_from_object("django.conf:settings", namespace="CELERY")

if "test" in sys.argv[1:]:
    app.conf.update(task_always_eager=True, task_serializer="pickle", result_serializer="pickle")

app.autodiscover_tasks()
