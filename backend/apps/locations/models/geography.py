"""Administrative geography: country, city, neighborhood.

A normalised hierarchy rather than free-text location strings on the listing.
With 5,000+ properties, faceted filtering by city and neighborhood is the
primary search path, and that only stays fast if those are indexed foreign
keys.

Coordinates are stored as plain decimals. No GIS extension and no map
integration in this phase - but the columns exist from the first migration, so
adding PostGIS later is an additive change rather than a data migration of
every listing.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel

LATITUDE_VALIDATORS = [MinValueValidator(Decimal("-90")), MaxValueValidator(Decimal("90"))]
LONGITUDE_VALIDATORS = [MinValueValidator(Decimal("-180")), MaxValueValidator(Decimal("180"))]


class CoordinatesMixin(models.Model):
    """Optional point location, shared by every geographic level."""

    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, validators=LATITUDE_VALIDATORS
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, validators=LONGITUDE_VALIDATORS
    )

    class Meta:
        abstract = True

    @property
    def has_coordinates(self) -> bool:
        return self.latitude is not None and self.longitude is not None


class Country(BaseModel, CoordinatesMixin):
    code = models.CharField(max_length=2, unique=True, help_text=_("ISO 3166-1 alpha-2."))
    name = models.CharField(max_length=100)
    phone_prefix = models.CharField(max_length=6, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("country")
        verbose_name_plural = _("countries")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class City(BaseModel, CoordinatesMixin):
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="cities")
    name = models.CharField(max_length=120, db_index=True)
    slug = models.SlugField(max_length=140, db_index=True)
    county = models.CharField(
        max_length=120, blank=True, help_text=_("County, province or state.")
    )
    is_featured = models.BooleanField(
        default=False, help_text=_("Surfaced on the public homepage.")
    )

    class Meta:
        verbose_name = _("city")
        verbose_name_plural = _("cities")
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["country", "slug"], name="unique_city_slug_per_country")
        ]

    def __str__(self) -> str:
        return self.name


class Neighborhood(BaseModel, CoordinatesMixin):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="neighborhoods")
    name = models.CharField(max_length=120, db_index=True)
    slug = models.SlugField(max_length=140, db_index=True)

    class Meta:
        verbose_name = _("neighborhood")
        verbose_name_plural = _("neighborhoods")
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["city", "slug"], name="unique_neighborhood_slug_per_city"
            )
        ]

    def __str__(self) -> str:
        return f"{self.name}, {self.city.name}"
