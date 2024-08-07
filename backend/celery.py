# backend/celery.py

from __future__ import absolute_import, unicode_literals
import os
import sys

from celery import Celery
from django.conf import settings

from settings.helpers import get_var

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

CELERY_BROKER = get_var("CELERY_BROKER") or get_var("REDIS_CACHE_HOST") or "redis://localhost:6379/0"
CELERY_BACKEND = get_var("CELERY_BACKEND") or get_var("REDIS_CACHE_HOST") or "redis://localhost:6379/0"

app = Celery("backend", broker=CELERY_BROKER, backend=CELERY_BACKEND)

app.config_from_object("django.conf:settings", namespace="CELERY")

if "test" in sys.argv[1:]:
    app.conf.update(task_always_eager=True, task_serializer="pickle", result_serializer="pickle")

app.autodiscover_tasks()
