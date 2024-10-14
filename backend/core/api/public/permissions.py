from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from django.conf import settings

SCOPES = {
    "clients:read",
    "clients:write",
    "invoices:read",
    "invoices:write",
    "receipts:read",
    "receipts:write",
    "clients:read",
    "clients:write",
    "emails:read",
    "emails:send",
    "profile:read",
    "profile:write",
    "api_keys:read",
    "api_keys:write",
    "team_permissions:read",
    "team_permissions:write",
    "team:invite",
    "team:kick",
    "account_defaults:write",
    "email_templates:read",
    "email_templates:write",
}

SCOPES_TREE = {
    "clients:read": {"clients:read"},
    "clients:write": {"clients:read", "clients:write"},
    "invoices:read": {"invoices:read"},
    "invoices:write": {"invoices:read", "invoices:write"},
    "profile:read": {"profile:read"},
    "profile:write": {"profile:read", "profile:write"},
    "api_keys:read": {"api_keys:read"},
    "api_keys:write": {"api_keys:read", "api_keys:write"},
    "team_permissions:read": {"team_permissions:read"},
    "team_permissions:write": {"team_permissions:read", "team_permissions:write"},
    "team:invite": {"team:invite"},
    "team:kick": {"team:kick", "team:invite"},
    "email_templates:read": {"email_templates:read"},
    "email_templates:write": {"email_templates:read", "email_templates:write"},
    "account_defaults:write": {"account_defaults:write"},
}

SCOPE_DESCRIPTIONS = {
    "clients": {"description": "Access customer details", "options": {"read": "Read only", "write": "Read and write"}},
    "invoices": {"description": "Access invoices", "options": {"read": "Read only", "write": "Read and write"}},
    "profile": {"description": "Access profile details", "options": {"read": "Read only", "write": "Read and write"}},
    "api_keys": {"description": "Access API keys", "options": {"read": "Read only", "write": "Read and write"}},
    "team_permissions": {"description": "Access team permissions", "options": {"read": "Read only", "write": "Read and write"}},
    "team": {"description": "Invite team members", "options": {"invite": "Invite members"}},
    "email_templates": {"description": "Access email templates", "options": {"read": "Read only", "write": "Read and write"}},
    "account_defaults": {"description": "Modify account defaults", "options": {"write": "Read and write"}},
}

if settings.BILLING_ENABLED:
    SCOPES.add("billing:manage")
    SCOPES_TREE["billing:manage"] = {"billing:manage"}
    SCOPE_DESCRIPTIONS["billing"] = {"description": "Access billing details + stripe", "options": {"manage": "Manage billing"}}


class IsSuperuser(BasePermission):
    def has_permission(self, request: Request, view: object) -> bool:
        return bool(request.user and request.user.is_superuser)
