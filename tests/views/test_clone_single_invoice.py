import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
django.setup()
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from backend.finance.models import Invoice
from tests.handler import ViewTestCase
from datetime import date

User = get_user_model()
from backend.finance.views.invoices.single.create import create_invoice_page_endpoint
from django.test import RequestFactory, TestCase


class CloneSingleInvoiceViews(TestCase):
    """
    Tests single invoice cloning and whether it verifies with prefilled data
    on the create invoice page.
    """

    def setUp(self):
        """
        Set up a test user and password, then create an initial invoice
        under the test user.
        """
        self.user = User.objects.create_user(username="testUser", password="Password")
        self.client.login(username="testUser", password="Password")

        self.original_invoice = Invoice.objects.create(
            owner=self.user,
            reference="INV-001",
            client_name="TestClient",
            sort_code="12-34-56",
            account_number="12345678",
            client_is_representative=False,
            currency="AUD",
            discount_amount=0,
            discount_percentage=0,
            date_due=date(2024, 6, 24),
            status="draft",
        )

    @patch("backend.finance.views.invoices.single.create.get_invoice_context")
    def test_clone_invoice_adds_prefill(self, mock_get_invoice_context):
        # create mock context dictionary
        mock_context = {
            "clients": [],
            "existing_products": [],
            "issue_date": "2025-06-24",
            "due_date": "2025-07-01",
        }
        mock_get_invoice_context.return_value = mock_context

        factory = RequestFactory()
        request = factory.get(f"/dashboard/invoices/single/create/?clone_from={self.original_invoice.id}")
        request.user = self.user

        # added to bypass errors & template crashes with dummy attributes etc
        setattr(request.user, "notification_count", 0)

        mock_team = MagicMock()
        mock_team.is_owner.return_value = True
        request.team = mock_team
        request.team_id = 1
        request.scope_strings = ["invoices:read", "finance:invoices:single:dashboard"]

        # call the view
        create_invoice_page_endpoint(request)

        # check prefill is added to context & match values
        self.assertEqual(mock_context["reference"], "INV-001-COPY")
        self.assertEqual(mock_context["account_number"], "12345678")
        self.assertEqual(mock_context["sort_code"], "12-34-56")
