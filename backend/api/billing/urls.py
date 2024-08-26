from django.urls import path

from .fetch import fetch_bill_table_by_month_endpoint

urlpatterns = [
    path("fetch/", fetch_bill_table_by_month_endpoint, name="fetch"),
]

app_name = "billing"
