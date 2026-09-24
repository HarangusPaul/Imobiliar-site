"""Development-scoped permissions."""

from __future__ import annotations

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.access.policy import Capability
from apps.access.selectors.roles import has_capability


class CanManageDevelopments(BasePermission):
    message = "Your role cannot manage developments."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return has_capability(request.user, Capability.DEVELOPMENT_MANAGE)
