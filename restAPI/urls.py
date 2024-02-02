from django.urls import path, include

urlpatterns = [
    path("clients/", include("restAPI.clients.urls")),
    path("receipts/", include("restAPI.receipts.urls")),
    path("invoices/", include("restAPI.invoices.urls")),
]

app_name = "restAPI"
