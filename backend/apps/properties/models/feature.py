"""Amenities and features.

Modelled as rows rather than boolean columns. A listing table with 60 boolean
amenity columns is unmaintainable, and the set grows with the market. Features
are grouped so the filter sidebar can render sections without hardcoding them.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class FeatureGroup(models.TextChoices):
    INTERIOR = "interior", _("Interior")
    BUILDING = "building", _("Building")
    OUTDOOR = "outdoor", _("Outdoor")
    UTILITIES = "utilities", _("Utilities")
    SECURITY = "security", _("Security")
    ACCESSIBILITY = "accessibility", _("Accessibility")


class Feature(BaseModel):
    code = models.SlugField(max_length=60, unique=True)
    name = models.CharField(max_length=100)
    group = models.CharField(
        max_length=20, choices=FeatureGroup.choices, default=FeatureGroup.INTERIOR, db_index=True
    )
    is_filterable = models.BooleanField(
        default=True, help_text=_("Appears in the public search filters.")
    )
    is_premium_filter = models.BooleanField(
        default=False,
        help_text=_("Filtering by this requires a subscription entitlement."),
    )
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = _("feature")
        verbose_name_plural = _("features")
        ordering = ["group", "sort_order", "name"]

    def __str__(self) -> str:
        return self.name
