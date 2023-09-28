from django.urls import reverse
from .handler import ViewTestCase


class InvoicesViewTestCase(ViewTestCase):
    def test_invoices_view_302_for_non_authenticated_users(self):
        response = self.client.get(reverse("invoices dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_invoices_view_200_for_authenticated_users(self):
        self.client.login(username="user", password="user")
        response = self.client.get(reverse("invoices dashboard"))

        # self.client.login(username="user", password="user")
        # response = self.client.get(reverse("invoices dashboard"))
        # self.assertEqual(response.status_code, 200)