"""Plans and the entitlements they carry.

Entitlements are data on the plan, not classes in code, for the same reason
roles are data: the product will add plans, and adding one must not require
touching apps.properties.

Money is modelled here only as a price *label* on a plan. There is no payment
concept in this phase - no transactions, no invoices, no provider references.
Subscription state is set administratively.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class BillingPeriod(models.TextChoices):
    MONTHLY = "monthly", _("Monthly")
    YEARLY = "yearly", _("Yearly")
    LIFETIME = "lifetime", _("Lifetime")


class Entitlement(models.TextChoices):
    """The questions the product can ask about a subscription.

    Every value here answers a concrete product question. Nothing is added
    speculatively.
    """

    PREMIUM_FILTERS = "premium_filters", _("Premium search filters")
    SUBSCRIBER_ONLY_FIELDS = "subscriber_only_fields", _("Subscriber-only listing fields")
    FULL_DOCUMENTS = "full_documents", _("Full property documents")
    SAVED_SEARCH_ALERTS = "saved_search_alerts", _("Saved-search alerts")
    EARLY_ACCESS_LISTINGS = "early_access_listings", _("Early access to new listings")
    CONTACT_DETAILS = "contact_details", _("Direct owner/agent contact details")


class Plan(BaseModel):
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    entitlements = models.JSONField(
        default=list, blank=True, help_text=_("Entitlement values granted by this plan.")
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Display price. No payment processing exists in this phase."),
    )
    currency = models.CharField(max_length=3, default="EUR")
    billing_period = models.CharField(
        max_length=16, choices=BillingPeriod.choices, default=BillingPeriod.MONTHLY
    )

    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(
        default=False, help_text=_("The implicit plan for accounts with no subscription.")
    )
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = _("plan")
        verbose_name_plural = _("plans")
        ordering = ["sort_order", "price"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_default"], condition=models.Q(is_default=True), name="single_default_plan"
            )
        ]

    def __str__(self) -> str:
        return self.name

    def grants(self, entitlement: str) -> bool:
        return entitlement in self.entitlements
