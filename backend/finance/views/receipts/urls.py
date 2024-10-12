from django.urls import path

from .dashboard import receipts_dashboard

urlpatterns = [path("", receipts_dashboard, name="dashboard")]

app_name = "receipts"
