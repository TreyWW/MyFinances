from django.urls import path

from billing.views.dashboard import billing_dashboard_endpoint, all_subscriptions_htmx_endpoint
from billing.views.stripe_misc import customer_client_portal_endpoint
from billing.views.stripe_webhooks import stripe_listener_webhook_endpoint

from .views.return_urls.success import stripe_success_return_endpoint
from .views.change_plan import change_plan_endpoint

urlpatterns = [
    path("dashboard/billing/", billing_dashboard_endpoint, name="dashboard"),
    path("api/billing/all_subscriptions/", all_subscriptions_htmx_endpoint, name="all_subscriptions"),
    # path("dashboard/billing/", RedirectView.as_view(url="/dashboard"), name="dashboard"),
    path("api/public/webhooks/receive/payments/stripe/", stripe_listener_webhook_endpoint, name="receive_stripe_webhook"),
    path("api/billing/stripe/change_plan/", change_plan_endpoint, name="change_plan"),
    path("dashboard/billing/stripe/portal/", customer_client_portal_endpoint, name="stripe_customer_portal"),
    path("dashboard/billing/stripe/checkout/response/success/", stripe_success_return_endpoint, name="stripe_checkout_success_response"),
    path("dashboard/billing/stripe/checkout/response/failed/", stripe_success_return_endpoint, name="stripe_checkout_failed_response"),
]

app_name = "billing"
