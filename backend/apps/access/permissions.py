"""DRF permission classes backed by role policy.

Domain apps compose these instead of testing role codes. core.permissions
supplies the generic shapes; this module supplies the product meaning.
"""

from __future__ import annotations

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.access.models import AccessArea
from apps.access.selectors.roles import can_reach_area, has_capability


class HasCapability(BasePermission):
    """Grants access when the view declares a capability the user holds.

    Usage::

        class PropertyCreateView(APIView):
            permission_classes = [IsAuthenticatedAndActive, HasCapability]
            required_capability = Capability.PROPERTY_CREATE
    """

    message = "Your role does not allow this action."

    def has_permission(self, request: Request, view: APIView) -> bool:
        capability = getattr(view, "required_capability", None)
        if capability is None:
            # Fail closed: a view that forgot to declare one gets nothing.
            return False
        return has_capability(request.user, capability)


class CanReachArea(BasePermission):
    """Zone-level gate. Views default to the dashboard area."""

    message = "This area is not available for your account."

    def has_permission(self, request: Request, view: APIView) -> bool:
        area = getattr(view, "access_area", AccessArea.DASHBOARD)
        return can_reach_area(request.user, area)


class IsDashboardUser(CanReachArea):
    """Convenience baseline for every /api/v1/dashboard/ view."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not (request.user and request.user.is_authenticated and request.user.is_active):
            return False
        return can_reach_area(request.user, AccessArea.DASHBOARD)
