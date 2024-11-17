from datetime import date

from django.urls import reverse, resolve

from backend.finance.models import Invoice
from tests.handler import ViewTestCase


class InvoicesViewTestCase(ViewTestCase):
    def setUp(self):
        super().setUp()

        self._invoices_dashboard_url = reverse("finance:invoices:single:dashboard")

    def test_invoices_view_302_for_non_authenticated_users(self):
        response = self.client.get(self._invoices_dashboard_url)
        self.assertEqual(response.status_code, 302)

    def test_invoices_view_200_for_authenticated_users(self):
        self.login_user()
        response = self.client.get(self._invoices_dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.login_to_team()
        response = self.client.get(self._invoices_dashboard_url)
        self.assertEqual(response.status_code, 200)

    def test_invoices_view_match_with_template(self):
        self.login_user()
        response = self.client.get(self._invoices_dashboard_url)
        self.assertTemplateUsed(response, "pages/invoices/single/dashboard/dashboard.html")

    def test_invoices_view_matches_with_urls_view(self):
        func = resolve("/dashboard/invoices/").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/dashboard/invoices/single/", self._invoices_dashboard_url)
        self.assertEqual("backend.finance.views.invoices.single.dashboard.invoices_single_dashboard_endpoint", func_name)


class InvoicesCreateTestCase(ViewTestCase):
    def setUp(self):
        super().setUp()

        self._invoices_create_url = reverse("finance:invoices:single:create")
        self.data = {
            "service_name[]": ["Service 1", "Service 2"],
            "hours[]": [2, 3],
            "price_per_hour[]": [50, 60],
            "date_due": "2022-01-01",
            "date_issued": "2021-12-01",
            "to_name": "Client Name",
            "to_company": "Client Company",
            "to_email": "Client Email",
            "to_address": "Client Address",
            "to_city": "Client City",
            "to_county": "Client County",
            "to_country": "Client Country",
            "from_name": "Self Name",
            "from_company": "Self Company",
            "from_address": "Self Address",
            "from_city": "Self City",
            "from_county": "Self County",
            "from_country": "Self Country",
            "notes": "Invoice Notes",
            "vat_number": "VAT-001",
            "reference": "INV-001",
            "sort_code": "123456",
            "account_number": "12345678",
            "account_holder_name": "Account Holder Name",
        }

    def test_invoices_create_302_for_non_authenticated_users(self):
        response = self.client.get(self._invoices_create_url)
        self.assertEqual(response.status_code, 302)

    def test_invoices_create_200_for_authenticated_users(self):
        self.login_user()
        response = self.client.get(self._invoices_create_url)
        self.assertEqual(response.status_code, 200)
        self.login_to_team()
        response = self.client.get(self._invoices_create_url)
        self.assertEqual(response.status_code, 200)

    def test_invoices_create_match_with_template(self):
        self.login_user()
        response = self.client.get(self._invoices_create_url)
        self.assertTemplateUsed(response, "pages/invoices/create/create_single.html")

    def test_invoices_create_matches_with_urls_view(self):
        func = resolve("/dashboard/invoices/single/create/").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/dashboard/invoices/single/create/", self._invoices_create_url)
        self.assertEqual("backend.finance.views.invoices.single.create.create_single_invoice_endpoint_handler", func_name)

    def test_invoices_create_invoice_from_post_data(self):
        self.login_user()

        self.client.post(self._invoices_create_url, self.data)

        invoices = Invoice.objects.filter(user=self.log_in_user)

        self.assertEqual(len(invoices), 1)
        invoice = invoices[0]

        self.assertEqual(invoice.date_due, date(2022, 1, 1))
        self.assertEqual(invoice.date_issued, date(2021, 12, 1))
        self.assertEqual(invoice.client_name, "Client Name")
        self.assertEqual(invoice.client_company, "Client Company")
        self.assertEqual(invoice.client_address, "Client Address")
        self.assertEqual(invoice.client_city, "Client City")
        self.assertEqual(invoice.client_county, "Client County")
        self.assertEqual(invoice.client_country, "Client Country")
        self.assertEqual(invoice.self_name, "Self Name")
        self.assertEqual(invoice.self_company, "Self Company")
        self.assertEqual(invoice.self_address, "Self Address")
        self.assertEqual(invoice.self_city, "Self City")
        self.assertEqual(invoice.self_county, "Self County")
        self.assertEqual(invoice.self_country, "Self Country")
        self.assertEqual(invoice.notes, "Invoice Notes")
        self.assertEqual(invoice.vat_number, "VAT-001")
        self.assertEqual(invoice.reference, "INV-001")
        self.assertEqual(invoice.sort_code, "123456")
        self.assertEqual(invoice.account_number, "12345678")
        self.assertEqual(invoice.account_holder_name, "Account Holder Name")

    def test_invoices_create_invoice_from_post_data_for_Teams(self):
        self.login_user()
        self.login_to_team()

        self.data["organization"] = self.created_team.pk

        self.client.post(self._invoices_create_url, self.data)

        invoices = Invoice.objects.filter(organization=self.log_in_user.logged_in_as_team)

        self.assertEqual(len(invoices), 1)
        invoice = invoices[0]

        self.assertEqual(invoice.organization, self.created_team)
