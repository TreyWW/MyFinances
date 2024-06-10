from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class IsSuperuser(BasePermission):
    def has_permission(self, request: Request, view: object) -> bool:
        return bool(request.user and request.user.is_superuser)
