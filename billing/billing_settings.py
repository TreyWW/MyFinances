import stripe

from settings.helpers import get_var

STRIPE_TEST_SECRET_KEY = get_var("STRIPE_TEST_SECRET_KEY")
STRIPE_LIVE_SECRET_KEY = get_var("STRIPE_LIVE_SECRET_KEY")
STRIPE_WEBHOOK_ENDPOINT_SECRET = get_var("STRIPE_WEBHOOK_ENDPOINT_SECRET")

STRIPE_MAIN_API_KEY = STRIPE_LIVE_SECRET_KEY if STRIPE_LIVE_SECRET_KEY else STRIPE_TEST_SECRET_KEY

STRIPE_LIVE_MODE = True if STRIPE_LIVE_SECRET_KEY else False

stripe.api_key = STRIPE_MAIN_API_KEY

NO_SUBSCRIPTION_PLAN_DENY_VIEW_NAMES: set[str] = {
    "clients:create",
    "file_storage:upload:start_batch",
    "file_storage:upload:end_batch",
    "file_storage:upload:add_to_batch",
    "file_storage:upload:dashboard",
    # "finance:invoices:single:manage_access",
    "finance:invoices:single:manage_access create",
    # "finance:invoices:single:manage_access delete",
    "finance:invoices:single:edit",
    "finance:invoices:single:create",
    "finance:invoices:recurring:create",
    "finance:invoices:recurring:edit",
    # APIS
    "teams:invite",
    "teams:create",
    "receipts:edit",
    "receipts:new",
    "finance:invoices:single:edit",
    "finance:invoices:single:edit discount",
    "finance:invoices:recurring:generate next invoice",
    "finance:invoices:recurring:edit",
    "finance:invoices:create:set_destination from",
    "finance:invoices:create:set_destination to",
    "finance:invoices:create:services add",
    "products:create",
    "public:clients:create",
    "public:invoices:create",
}
