"""The vocabulary of a listing.

Three independent state axes, kept separate because they answer different
questions and change for different reasons:

* publication - is this listing visible on the public website?
* availability - can this thing still be transacted?
* transaction - is it for sale or for rent?

Collapsing them into one status field is the usual mistake. A listing can be
published and reserved; it can be archived while still marked sold; a rental
and a sale share every publication rule.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class PublicationStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    PENDING_REVIEW = "pending_review", _("Pending review")
    PUBLISHED = "published", _("Published")
    ARCHIVED = "archived", _("Archived")


class AvailabilityStatus(models.TextChoices):
    AVAILABLE = "available", _("Available")
    RESERVED = "reserved", _("Reserved")
    SOLD = "sold", _("Sold")
    RENTED = "rented", _("Rented")
    UNAVAILABLE = "unavailable", _("Unavailable")


class TransactionType(models.TextChoices):
    SALE = "sale", _("For sale")
    RENT = "rent", _("For rent")


class PropertyType(models.TextChoices):
    APARTMENT = "apartment", _("Apartment")
    STUDIO = "studio", _("Studio")
    HOUSE = "house", _("House")
    VILLA = "villa", _("Villa")
    LAND = "land", _("Land")
    OFFICE = "office", _("Office")
    COMMERCIAL = "commercial", _("Commercial space")
    INDUSTRIAL = "industrial", _("Industrial space")
    GARAGE = "garage", _("Garage or parking")


class Currency(models.TextChoices):
    EUR = "EUR", _("Euro")
    RON = "RON", _("Romanian leu")
    USD = "USD", _("US dollar")


class RentPeriod(models.TextChoices):
    """Only meaningful when transaction_type is RENT."""

    MONTH = "month", _("Per month")
    WEEK = "week", _("Per week")
    DAY = "day", _("Per day")


#: Availability values that still allow a listing to be shown publicly.
PUBLICLY_LISTABLE_AVAILABILITY = frozenset(
    {AvailabilityStatus.AVAILABLE, AvailabilityStatus.RESERVED}
)

#: Publication transitions the domain permits. Enforced in services/publishing.
ALLOWED_PUBLICATION_TRANSITIONS: dict[str, frozenset[str]] = {
    PublicationStatus.DRAFT: frozenset(
        {PublicationStatus.PENDING_REVIEW, PublicationStatus.PUBLISHED, PublicationStatus.ARCHIVED}
    ),
    PublicationStatus.PENDING_REVIEW: frozenset(
        {PublicationStatus.PUBLISHED, PublicationStatus.DRAFT, PublicationStatus.ARCHIVED}
    ),
    PublicationStatus.PUBLISHED: frozenset(
        {PublicationStatus.ARCHIVED, PublicationStatus.DRAFT}
    ),
    PublicationStatus.ARCHIVED: frozenset({PublicationStatus.DRAFT}),
}
