"""A user's subscription record and its lifecycle."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

from apps.subscriptions.models.plan import Plan


class SubscriptionStatus(models.TextChoices):
    TRIALING = "trialing", _("Trialing")
    ACTIVE = "active", _("Active")
    PAST_DUE = "past_due", _("Past due")
    CANCELLED = "cancelled", _("Cancelled")
    EXPIRED = "expired", _("Expired")


class SubscriptionQuerySet(models.QuerySet):
    def current(self) -> "SubscriptionQuerySet":
        """Subscriptions that are in force right now."""
        now = timezone.now()
        return self.filter(
            status__in=[SubscriptionStatus.TRIALING, SubscriptionStatus.ACTIVE],
            starts_at__lte=now,
        ).filter(models.Q(ends_at__isnull=True) | models.Q(ends_at__gt=now))


class Subscription(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")

    status = models.CharField(
        max_length=16, choices=SubscriptionStatus.choices, default=SubscriptionStatus.ACTIVE,
        db_index=True,
    )
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(
        null=True, blank=True, help_text=_("Null means open-ended.")
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)

    note = models.CharField(
        max_length=255, blank=True, help_text=_("Why this subscription was granted or changed.")
    )

    objects = SubscriptionQuerySet.as_manager()

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")
        ordering = ["-starts_at"]
        indexes = [models.Index(fields=["user", "status", "-starts_at"])]

    def __str__(self) -> str:
        return f"{self.user} - {self.plan.code} ({self.status})"

    @property
    def is_current(self) -> bool:
        now = timezone.now()
        return (
            self.status in {SubscriptionStatus.TRIALING, SubscriptionStatus.ACTIVE}
            and self.starts_at <= now
            and (self.ends_at is None or self.ends_at > now)
        )
