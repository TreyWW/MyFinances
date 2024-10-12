from django.views.decorators.http import require_GET

from backend.decorators import web_require_scopes
from backend.core.types.requests import WebRequest


@require_GET
@web_require_scopes("email_templates:read")
def get_current_email_template(request: WebRequest): ...
