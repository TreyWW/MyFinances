from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .handler import login_user, test_with_prints

from backend.urls import urlpatterns


class TestInvoices(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='user')

    def test_invoices_logged_in(self):
        test_with_prints(self, "invoices dashboard", 200, True)

    def test_invoices_not_logged_in(self):
        test_with_prints(self, "invoices dashboard", 302, False)