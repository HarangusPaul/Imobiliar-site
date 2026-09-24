"""The listing.

Design notes that matter at 5,000+ rows:

* The public list query filters on publication_status, availability_status,
  transaction_type, property_type, city and price, and orders by published_at.
  Those paths are covered by the composite indexes declared below rather than
  left to chance.
* description and short_description live on the row, but the public *card*
  serializer never selects description. See api/serializers/public.py.
* cover_image is a denormalised pointer into apps.media so a 24-card grid
  costs one extra join instead of twenty-four media queries.
* Price is a Decimal. Never a float.
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel, SoftDeleteModel

from apps.properties.models.enums import (
    PUBLICLY_LISTABLE_AVAILABILITY,
    AvailabilityStatus,
    Currency,
    PropertyType,
    PublicationStatus,
    RentPeriod,
    TransactionType,
)
from apps.properties.models.feature import Feature


class PropertyQuerySet(models.QuerySet):
    def published(self) -> "PropertyQuerySet":
        """The public visibility rule, defined once.

        Everything the anonymous website can see passes through here.
        """
        return self.filter(
            publication_status=PublicationStatus.PUBLISHED,
            availability_status__in=PUBLICLY_LISTABLE_AVAILABILITY,
            published_at__isnull=False,
        )

    def for_card(self) -> "PropertyQuerySet":
        """Exactly what a listing card needs, and nothing more."""
        return self.select_related("address__city", "address__neighborhood", "cover_image").only(
            "uuid", "title", "slug", "short_description", "property_type", "transaction_type",
            "availability_status", "price", "currency", "rent_period", "price_on_request",
            "rooms", "bathrooms", "usable_area", "floor", "published_at", "is_featured",
            "address__id", "address__is_exact_public",
            "address__city__name", "address__city__slug",
            "address__neighborhood__name", "address__neighborhood__slug",
            "cover_image__id", "cover_image__file_key", "cover_image__alt_text",
        )

    def for_detail(self) -> "PropertyQuerySet":
        return self.select_related(
            "address__city", "address__neighborhood", "address__city__country", "agent"
        ).prefetch_related("features")


class Property(BaseModel, SoftDeleteModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    reference_code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text=_("Human-quotable identifier used on the phone and in adverts."),
    )

    short_description = models.CharField(
        max_length=300, blank=True, help_text=_("One or two lines, shown on the listing card.")
    )
    description = models.TextField(blank=True)

    property_type = models.CharField(max_length=20, choices=PropertyType.choices, db_index=True)
    transaction_type = models.CharField(
        max_length=10, choices=TransactionType.choices, db_index=True
    )
    publication_status = models.CharField(
        max_length=20,
        choices=PublicationStatus.choices,
        default=PublicationStatus.DRAFT,
        db_index=True,
    )
    availability_status = models.CharField(
        max_length=20,
        choices=AvailabilityStatus.choices,
        default=AvailabilityStatus.AVAILABLE,
        db_index=True,
    )

    address = models.ForeignKey(
        "locations.Address", on_delete=models.PROTECT, related_name="properties"
    )

    price = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.EUR)
    rent_period = models.CharField(
        max_length=10,
        choices=RentPeriod.choices,
        blank=True,
        help_text=_("Required for rentals, empty for sales."),
    )
    price_on_request = models.BooleanField(
        default=False, help_text=_("Hides the figure publicly; the value is still stored.")
    )

    rooms = models.PositiveSmallIntegerField(null=True, blank=True, db_index=True)
    bathrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    usable_area = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Square metres."),
    )
    total_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text=_("Built or land area, in square metres."),
    )
    floor = models.SmallIntegerField(
        null=True, blank=True, help_text=_("0 is ground floor; negative is basement.")
    )
    total_floors = models.PositiveSmallIntegerField(null=True, blank=True)
    year_built = models.PositiveSmallIntegerField(null=True, blank=True)

    features = models.ManyToManyField(Feature, blank=True, related_name="properties")

    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="listings",
        help_text=_("The account responsible for this listing."),
    )

    cover_image = models.ForeignKey(
        "media.MediaAsset",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cover_for_properties",
        help_text=_("Denormalised so listing grids need no media query per row."),
    )

    is_featured = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = PropertyQuerySet.as_manager()
    all_objects = models.Manager.from_queryset(PropertyQuerySet)()

    class Meta:
        verbose_name = _("property")
        verbose_name_plural = _("properties")
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(
                fields=["publication_status", "availability_status", "-published_at"],
                name="prop_public_feed_idx",
            ),
            models.Index(
                fields=["transaction_type", "property_type", "price"],
                name="prop_type_price_idx",
            ),
            models.Index(fields=["agent", "publication_status"], name="prop_agent_status_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.reference_code} - {self.title}"

    @property
    def is_public(self) -> bool:
        return (
            self.publication_status == PublicationStatus.PUBLISHED
            and self.availability_status in PUBLICLY_LISTABLE_AVAILABILITY
            and self.published_at is not None
        )

    @property
    def price_per_square_metre(self) -> Decimal | None:
        if not self.usable_area or self.usable_area <= 0:
            return None
        return (self.price / self.usable_area).quantize(Decimal("0.01"))
