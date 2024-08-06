# backend/celery.py

from __future__ import absolute_import, unicode_literals
import os
import sys

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

app = Celery("backend")

app.config_from_object("django.conf:settings", namespace="CELERY")

if "test" in sys.argv[1:]:
    app.conf.update(task_always_eager=True, task_serializer="pickle", result_serializer="pickle")

app.autodiscover_tasks()
