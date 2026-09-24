"""Units, unit types, and the link between a unit and a public listing.

The Unit/Property relationship is the important design decision in this app.

A Unit is inventory: apartment 4B exists whether or not anyone is selling it
today, it has a fixed area and layout, and it belongs to a floor forever.
A Property is a listing: it has marketing copy, a price that changes, a
publication workflow, a responsible agent, and it may be withdrawn and
relisted.

They are therefore separate tables joined by an optional OneToOne from Unit to
Property. This gives us:

* a development whose inventory is fully modelled while nothing is published;
* units that are sold internally and never appear on the public site;
* a listing that can be archived without destroying the unit record;
* one place (Unit.availability) that stays true regardless of listing state.

Merging them would force every unit to carry listing machinery, and would make
"which apartments are left in Building A" a question about publication status.

UnitType is the repeated layout: in a development, the same two-room plan may
occur on fifteen floors. Modelling it once means the layout drawing, the area
and the room count are stored once, not fifteen times.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

from apps.developments.models.project import Development, Floor


class UnitAvailability(models.TextChoices):
    """Inventory truth, independent of whether a listing exists."""

    AVAILABLE = "available", _("Available")
    RESERVED = "reserved", _("Reserved")
    SOLD = "sold", _("Sold")
    RENTED = "rented", _("Rented")
    NOT_FOR_SALE = "not_for_sale", _("Not for sale")


class UnitType(BaseModel):
    """A repeated layout within a development."""

    development = models.ForeignKey(
        Development, on_delete=models.CASCADE, related_name="unit_types"
    )
    code = models.CharField(max_length=40, help_text=_("Type A, 2R-60, and so on."))
    name = models.CharField(max_length=120)

    rooms = models.PositiveSmallIntegerField(default=1)
    bathrooms = models.PositiveSmallIntegerField(default=1)
    usable_area = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    built_area = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    balcony_area = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    layout = models.ForeignKey(
        "media.MediaAsset", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="layout_for_unit_types",
        help_text=_("The apartment layout drawing, stored once for every unit of this type."),
    )

    class Meta:
        verbose_name = _("unit type")
        verbose_name_plural = _("unit types")
        ordering = ["development", "rooms", "usable_area"]
        constraints = [
            models.UniqueConstraint(
                fields=["development", "code"], name="unique_unit_type_code_per_development"
            )
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class UnitQuerySet(models.QuerySet):
    def available(self) -> "UnitQuerySet":
        return self.filter(availability=UnitAvailability.AVAILABLE)

    def publicly_listed(self) -> "UnitQuerySet":
        """Units that currently have a published listing behind them."""
        return self.filter(
            listing__isnull=False, listing__publication_status="published"
        )


class Unit(BaseModel):
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name="units")
    unit_type = models.ForeignKey(
        UnitType, on_delete=models.PROTECT, null=True, blank=True, related_name="units"
    )

    number = models.CharField(max_length=30, help_text=_("Apartment number, e.g. 4B."))
    availability = models.CharField(
        max_length=16, choices=UnitAvailability.choices,
        default=UnitAvailability.AVAILABLE, db_index=True,
    )

    # Per-unit overrides. Null means "inherit from unit_type".
    usable_area = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    rooms = models.PositiveSmallIntegerField(null=True, blank=True)
    orientation = models.CharField(
        max_length=20, blank=True, help_text=_("North, South-West, and so on.")
    )

    price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Developer price. The listing price may differ."),
    )
    currency = models.CharField(max_length=3, default="EUR")

    listing = models.OneToOneField(
        "properties.Property",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="unit",
        help_text=_("The public listing for this unit, when it should appear on the portal."),
    )

    objects = UnitQuerySet.as_manager()

    class Meta:
        verbose_name = _("unit")
        verbose_name_plural = _("units")
        ordering = ["floor", "number"]
        constraints = [
            models.UniqueConstraint(fields=["floor", "number"], name="unique_unit_per_floor")
        ]
        indexes = [models.Index(fields=["availability", "floor"])]

    def __str__(self) -> str:
        return f"{self.floor.building.name} {self.number}"

    @property
    def development(self) -> Development:
        return self.floor.building.development

    @property
    def effective_rooms(self) -> int | None:
        return self.rooms if self.rooms is not None else getattr(self.unit_type, "rooms", None)

    @property
    def effective_usable_area(self) -> Decimal | None:
        if self.usable_area is not None:
            return self.usable_area
        return getattr(self.unit_type, "usable_area", None)

    @property
    def is_publicly_listed(self) -> bool:
        return self.listing_id is not None and self.listing.is_public
