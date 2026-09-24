"""Generic permission primitives.

These express *shapes* of access control, never product policy. "Who counts as
an agent" and "what a staff member may do" belong to ``apps/access``; "what a
paying subscriber may see" belongs to ``apps/subscriptions``.
"""

from __future__ import annotations

from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAuthenticatedAndActive(BasePermission):
    """Authenticated, and the account has not been disabled."""

    message = "An active authenticated account is required."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.is_active)


class ReadOnly(BasePermission):
    """Allows only safe methods. Compose with others via ``|``."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.method in SAFE_METHODS


class IsOwner(BasePermission):
    """Object-level ownership check.

    The view declares which attribute holds the owner via ``owner_field``;
    ``core`` does not hardcode any domain relation name.
    """

    message = "You do not have access to this object."
    default_owner_field = "user"

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        field = getattr(view, "owner_field", self.default_owner_field)
        owner = obj
        for part in field.split("__"):
            owner = getattr(owner, part, None)
            if owner is None:
                return False
        return owner == request.user


class DenyAll(BasePermission):
    """Explicit closed default.

    Used as the baseline for ``/api/v1/internal/`` so a newly added internal
    view is unreachable until somebody deliberately opens it.
    """

    message = "This endpoint is not available."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return False
