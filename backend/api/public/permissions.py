from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from backend.api.public import APIAuthToken

SCOPES = {
    "clients:read",
    "clients:write",
    "invoices:read",
    "invoices:write",
    "profile:read",
    "profile:write",
    "api_keys:read",
    "api_keys:write",
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
}

SCOPE_DESCRIPTIONS = {
    "clients": {"description": "Access customer details", "options": {"read": "Read only", "write": "Read and write"}},
    "invoices": {"description": "Access invoices", "options": {"read": "Read only", "write": "Read and write"}},
    "profile": {"description": "Access user profile", "options": {"read": "Read only", "write": "Read and write"}},
    "api_keys": {"description": "Access API keys", "options": {"read": "Read only", "write": "Read and write"}},
}


class IsSuperuser(BasePermission):
    def has_permission(self, request: Request, view: object) -> bool:
        return bool(request.user and request.user.is_superuser)


class HasScopePermission(BasePermission):
    def has_permission(self, request, view):
        required_scopes = getattr(view, "required_scopes", [])

        if not required_scopes:
            return True

        token = request.auth
        if not token or not isinstance(token, APIAuthToken):
            return False
        user_scopes = token.scopes  # assuming token has a `scopes` attribute
        return all(scope in user_scopes for scope in required_scopes)
