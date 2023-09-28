from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .handler import login_user, test_with_prints

from backend.urls import urlpatterns


class TestIndex(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='user')

    def test_invoices_not_logged_in(self):
        test_with_prints(self,"index", 200, False)

    def test_index_logged_in(self):
        test_with_prints(self,"index", 200, True)

    def test_logout(self):
        login_user(self)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)