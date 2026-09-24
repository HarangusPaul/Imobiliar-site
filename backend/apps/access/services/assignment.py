"""Role assignment use cases."""

from __future__ import annotations

from django.db import transaction

from core.api.exceptions import DomainError

from apps.access.models import Role, RoleAssignment
from apps.access.policy import DEFAULT_ROLE_CODE, SYSTEM_ROLE_DEFINITIONS


class RoleNotFoundError(DomainError):
    code = "role_not_found"
    message = "The requested role does not exist."
    status_code = 404


@transaction.atomic
def ensure_system_roles() -> None:
    """Idempotently create/refresh the seeded roles.

    Called by the seed command and by tests. Custom roles created through the
    dashboard are never touched.
    """
    for definition in SYSTEM_ROLE_DEFINITIONS:
        Role.objects.update_or_create(
            code=definition["code"],
            defaults={
                "name": definition["name"],
                "description": definition["description"],
                "areas": definition["areas"],
                "permissions": definition["permissions"],
                "priority": definition["priority"],
                "is_system": True,
            },
        )


@transaction.atomic
def assign_role(user, *, code: str, granted_by=None, note: str = "") -> RoleAssignment:
    try:
        role = Role.objects.get(code=code)
    except Role.DoesNotExist as exc:
        raise RoleNotFoundError(f"No role with code {code}.") from exc

    assignment, _created = RoleAssignment.objects.get_or_create(
        user=user, role=role, defaults={"granted_by": granted_by, "note": note}
    )
    return assignment


def assign_default_role(user, *, granted_by=None):
    """Called by apps.accounts on registration.

    Self-heals if the seed has not run yet, so a fresh database cannot produce
    role-less accounts.
    """
    if not Role.objects.filter(code=DEFAULT_ROLE_CODE).exists():
        ensure_system_roles()
    return assign_role(user, code=DEFAULT_ROLE_CODE, granted_by=granted_by)


@transaction.atomic
def revoke_role(user, *, code: str) -> None:
    RoleAssignment.objects.filter(user=user, role__code=code).delete()
