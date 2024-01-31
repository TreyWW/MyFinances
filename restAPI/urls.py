from django.urls import path, include

urlpatterns = [
    path("clients/", include("restAPI.clients.urls")),
    path("receipts/", include("restAPI.receipts.urls")),
    # path("invoices/", include("restAPI.invoices.urls")),
    #     path("products/", include("restAPI.products.urls")),
    #     path("currency_converter/", include("restAPI.currency_converter.urls")),
]

app_name = "restAPI"
