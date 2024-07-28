# backend/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

app = Celery("backend")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
