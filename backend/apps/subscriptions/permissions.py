"""Entitlement-based DRF permissions.

Distinct from apps.access on purpose: a role says what kind of actor you are,
an entitlement says what you have paid for. A staff member with no
subscription still administers the platform; a client on a premium plan is
still a client.
"""

from __future__ import annotations

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.subscriptions.selectors.entitlements import has_entitlement


class HasEntitlement(BasePermission):
    """Views declare the attribute required_entitlement."""

    message = "Your current plan does not include this feature."

    def has_permission(self, request: Request, view: APIView) -> bool:
        entitlement = getattr(view, "required_entitlement", None)
        if entitlement is None:
            return False
        return has_entitlement(request.user, entitlement)
