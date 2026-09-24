"""Read-side queries for accounts.

Selectors are the only place that builds querysets. Views and serializers
consume them; they never assemble filters inline. This keeps query shape,
index usage and prefetching reviewable in one file per domain.
"""

from __future__ import annotations

from django.db.models import QuerySet

from apps.accounts.models import AccountStatus, User


def get_by_phone(phone_number: str) -> User | None:
    return User.objects.filter(phone_number=phone_number).first()


def get_by_uuid(uuid: str) -> User | None:
    return User.objects.filter(uuid=uuid).first()


def active_users() -> QuerySet[User]:
    return User.objects.filter(is_active=True, status=AccountStatus.ACTIVE)


def dashboard_user_list() -> QuerySet[User]:
    """Users as the dashboard lists them, with roles preloaded.

    ``role_assignments`` is defined by apps.access; naming it here is a read
    optimisation, not a dependency on how roles work.
    """
    return User.objects.prefetch_related("role_assignments__role").order_by("-created_at")
