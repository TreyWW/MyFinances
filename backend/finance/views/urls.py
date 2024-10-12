from django.urls import path
from django.urls.conf import include

from backend.finance.views.invoices.single.dashboard import invoices_single_dashboard_endpoint

urlpatterns = [
    path("invoices/", include("backend.finance.views.invoices.urls")),
    path("reports/", include("backend.finance.views.reports.urls")),
    path("receipts/", include("backend.finance.views.receipts.urls")),
    path("", invoices_single_dashboard_endpoint),
]

app_name = "finance"
