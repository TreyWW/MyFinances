from .auth.passwords import set
from .other import index, errors
from .auth import login
from .settings import view as settings_view, teams
from .invoices import dashboard as invoices_dashboard, create, view as invoices_view, manage_access
from .clients import dashboard as clients_dashboard, create as create_client
from .receipts import dashboard as receipts_dashboard
