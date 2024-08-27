from django.urls import path

from .fetch import fetch_bill_table_by_month_endpoint
from .change_plan import change_plan_endpoint

urlpatterns = [
    path("fetch/", fetch_bill_table_by_month_endpoint, name="fetch"),
    path("change_plan/", change_plan_endpoint, name="change_plan"),
]

app_name = "billing"
