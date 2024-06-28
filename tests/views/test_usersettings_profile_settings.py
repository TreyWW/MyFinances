import os

from django.contrib.messages import get_messages
from django.urls import reverse

from backend.models import UserSettings
from tests.handler import ViewTestCase, create_mock_image

# class UserSettingsProfileSettingsViewTestCase(ViewTestCase):
#
