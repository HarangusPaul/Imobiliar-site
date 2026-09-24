"""A concrete street address.

Addresses are their own table, shared by properties and developments, because
the same physical address can back a listing and a project, and because street
detail is frequently withheld from the public view while city and neighborhood
are shown.

Visibility is an address-level decision (is_exact_public), not a per-listing
flag, so the rule cannot drift between the two consumers.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

from apps.locations.models.geography import City, CoordinatesMixin, Neighborhood


class Address(BaseModel, CoordinatesMixin):
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="addresses")
    neighborhood = models.ForeignKey(
        Neighborhood,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="addresses",
    )

    street = models.CharField(max_length=180, blank=True)
    street_number = models.CharField(max_length=30, blank=True)
    building_identifier = models.CharField(
        max_length=60, blank=True, help_text=_("Block, entrance or staircase.")
    )
    postal_code = models.CharField(max_length=20, blank=True)

    is_exact_public = models.BooleanField(
        default=False,
        help_text=_("When false, public responses expose only city and neighborhood."),
    )

    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("addresses")
        indexes = [models.Index(fields=["city", "neighborhood"])]

    def __str__(self) -> str:
        return self.public_label if not self.is_exact_public else self.full_label

    @property
    def full_label(self) -> str:
        """Everything known. Dashboard and internal use only."""
        parts = [
            " ".join(p for p in (self.street, self.street_number) if p),
            self.building_identifier,
            self.neighborhood.name if self.neighborhood_id else "",
            self.city.name,
        ]
        return ", ".join(p for p in parts if p)

    @property
    def public_label(self) -> str:
        """What an unauthenticated visitor is allowed to see."""
        parts = [self.neighborhood.name if self.neighborhood_id else "", self.city.name]
        return ", ".join(p for p in parts if p)
