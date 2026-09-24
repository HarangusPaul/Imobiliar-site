"""Subscription state transitions.

Administrative only in this phase: staff grant, change and cancel
subscriptions. There is deliberately no payment concept anywhere in this app.
When one is introduced it becomes a caller of these functions, not a rewrite
of them.
"""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from core.api.exceptions import ConflictError, DomainError

from apps.subscriptions.models import Plan, Subscription, SubscriptionStatus


class PlanNotFoundError(DomainError):
    code = "plan_not_found"
    message = "The requested plan does not exist."
    status_code = 404


@transaction.atomic
def grant_subscription(*, user, plan_code: str, ends_at=None, note: str = "") -> Subscription:
    """Put a user on a plan, superseding any subscription in force.

    One current subscription per user is a rule of this domain; overlapping
    entitlements would make has_entitlement ambiguous.
    """
    try:
        plan = Plan.objects.get(code=plan_code, is_active=True)
    except Plan.DoesNotExist as exc:
        raise PlanNotFoundError(f"No active plan with code {plan_code}.") from exc

    Subscription.objects.current().filter(user=user).update(
        status=SubscriptionStatus.EXPIRED, ends_at=timezone.now()
    )

    return Subscription.objects.create(
        user=user,
        plan=plan,
        status=SubscriptionStatus.ACTIVE,
        starts_at=timezone.now(),
        ends_at=ends_at,
        note=note,
    )


@transaction.atomic
def cancel_subscription(subscription: Subscription, *, immediate: bool = False) -> Subscription:
    if subscription.status == SubscriptionStatus.CANCELLED:
        raise ConflictError("This subscription is already cancelled.")

    subscription.status = SubscriptionStatus.CANCELLED
    subscription.cancelled_at = timezone.now()
    if immediate:
        subscription.ends_at = timezone.now()
    subscription.save(update_fields=["status", "cancelled_at", "ends_at", "updated_at"])
    return subscription


@transaction.atomic
def expire_due_subscriptions() -> int:
    """Move past-end subscriptions to EXPIRED. Driven by a scheduled task."""
    return Subscription.objects.filter(
        status__in=[SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING],
        ends_at__lte=timezone.now(),
    ).update(status=SubscriptionStatus.EXPIRED)
