"""Read-side access questions.

One import surface for "what may this user do", so no other app ever joins
across RoleAssignment by hand.
"""

from __future__ import annotations

from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet

from apps.access.models import Role, RoleAssignment


def roles_for(user) -> QuerySet[Role]:
    if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return Role.objects.none()
    return Role.objects.filter(assignments__user=user).order_by("priority")


def role_codes_for(user) -> list[str]:
    return list(roles_for(user).values_list("code", flat=True))


def capabilities_for(user) -> set[str]:
    """Union of every capability granted by every role the user holds."""
    granted: set[str] = set()
    for permissions in roles_for(user).values_list("permissions", flat=True):
        granted.update(permissions or [])
    return granted


def has_capability(user, capability: str) -> bool:
    if getattr(user, "is_superuser", False):
        return True
    return capability in capabilities_for(user)


def can_reach_area(user, area: str) -> bool:
    if getattr(user, "is_superuser", False):
        return True
    return any(area in (areas or []) for areas in roles_for(user).values_list("areas", flat=True))


def assignments_for(user) -> QuerySet[RoleAssignment]:
    return RoleAssignment.objects.filter(user=user).select_related("role", "granted_by")
