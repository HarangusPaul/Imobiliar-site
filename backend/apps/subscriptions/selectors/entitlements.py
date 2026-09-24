"""The entitlement question, answered in exactly one place.

Other apps must never join across Subscription. apps.properties asks
has_entitlement(user, Entitlement.PREMIUM_FILTERS) and gets a boolean; it does
not learn what a plan is.
"""

from __future__ import annotations

from django.db.models import QuerySet

from apps.subscriptions.models import Entitlement, Plan, Subscription


def current_subscription(user) -> Subscription | None:
    if not user or not getattr(user, "is_authenticated", False):
        return None
    return (
        Subscription.objects.current()
        .filter(user=user)
        .select_related("plan")
        .order_by("-starts_at")
        .first()
    )


def default_plan() -> Plan | None:
    return Plan.objects.filter(is_default=True, is_active=True).first()


def effective_plan(user) -> Plan | None:
    """The plan in force: the current subscription, otherwise the default plan.

    Anonymous visitors and users who never subscribed both land on the default
    plan, so callers need no null-handling special case.
    """
    subscription = current_subscription(user)
    return subscription.plan if subscription else default_plan()


def entitlements_for(user) -> set[str]:
    plan = effective_plan(user)
    return set(plan.entitlements or []) if plan else set()


def has_entitlement(user, entitlement: str) -> bool:
    """Single authority for subscriber-gated behaviour."""
    if getattr(user, "is_superuser", False):
        return True
    return entitlement in entitlements_for(user)


def can_use_premium_filters(user) -> bool:
    return has_entitlement(user, Entitlement.PREMIUM_FILTERS)


def can_see_subscriber_only_fields(user) -> bool:
    return has_entitlement(user, Entitlement.SUBSCRIBER_ONLY_FIELDS)


def active_plans() -> QuerySet[Plan]:
    return Plan.objects.filter(is_active=True).order_by("sort_order", "price")


def subscription_history(user) -> QuerySet[Subscription]:
    return Subscription.objects.filter(user=user).select_related("plan").order_by("-starts_at")
