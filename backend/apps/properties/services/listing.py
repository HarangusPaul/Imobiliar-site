"""Create and update listings.

Everything a write touches is here: slug and reference generation,
cross-field validation, feature assignment and the audit trail. The API layer
supplies validated field values and an actor, nothing more.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from core.api.exceptions import NotAllowedError
from core.validation import unique_slugify

from apps.access.policy import Capability
from apps.access.selectors.roles import has_capability
from apps.properties.models import Feature, Property, PublicationStatus
from apps.properties.validators import (
    validate_areas,
    validate_floors,
    validate_price,
    validate_rent_period,
)


@dataclass(slots=True)
class PropertyInput:
    title: str
    property_type: str
    transaction_type: str
    address_id: int
    price: Decimal
    currency: str = "EUR"
    rent_period: str = ""
    short_description: str = ""
    description: str = ""
    rooms: int | None = None
    bathrooms: int | None = None
    usable_area: Decimal | None = None
    total_area: Decimal | None = None
    floor: int | None = None
    total_floors: int | None = None
    year_built: int | None = None
    price_on_request: bool = False
    feature_codes: list[str] = field(default_factory=list)
    agent_id: int | None = None


def _validate(data: PropertyInput) -> None:
    """Cross-field business rules, applied identically on create and update."""
    validate_price(data.price, transaction_type=data.transaction_type)
    validate_rent_period(data.rent_period, transaction_type=data.transaction_type)
    validate_areas(data.usable_area, data.total_area)
    validate_floors(data.floor, data.total_floors)


def _generate_reference_code() -> str:
    """A short, human-quotable code.

    Sequential within the year so staff can read it aloud, but derived from
    the row count rather than the primary key so it is not a database id.
    """
    year = timezone.now().year
    sequence = Property.all_objects.filter(created_at__year=year).count() + 1
    return f"P{year % 100:02d}-{sequence:05d}"


@transaction.atomic
def create_property(data: PropertyInput, *, actor) -> Property:
    if not has_capability(actor, Capability.PROPERTY_CREATE):
        raise NotAllowedError("Your role cannot create listings.")
    _validate(data)

    prop = Property(
        title=data.title.strip(),
        slug=unique_slugify(
            data.title, exists=lambda s: Property.all_objects.filter(slug=s).exists()
        ),
        reference_code=_generate_reference_code(),
        short_description=data.short_description.strip(),
        description=data.description,
        property_type=data.property_type,
        transaction_type=data.transaction_type,
        publication_status=PublicationStatus.DRAFT,
        address_id=data.address_id,
        price=data.price,
        currency=data.currency,
        rent_period=data.rent_period,
        price_on_request=data.price_on_request,
        rooms=data.rooms,
        bathrooms=data.bathrooms,
        usable_area=data.usable_area,
        total_area=data.total_area,
        floor=data.floor,
        total_floors=data.total_floors,
        year_built=data.year_built,
        agent_id=data.agent_id or actor.pk,
    )
    prop.full_clean(exclude=["cover_image"])
    prop.save()
    _sync_features(prop, data.feature_codes)

    _record(prop, action="property.created", actor=actor, metadata={"title": prop.title})
    return prop


@transaction.atomic
def update_property(prop: Property, data: PropertyInput, *, actor) -> Property:
    if not _may_edit(actor, prop):
        raise NotAllowedError("You cannot edit this listing.")
    _validate(data)

    changed: dict[str, Any] = {}
    for name in (
        "title", "short_description", "description", "property_type", "transaction_type",
        "price", "currency", "rent_period", "price_on_request", "rooms", "bathrooms",
        "usable_area", "total_area", "floor", "total_floors", "year_built",
    ):
        new_value = getattr(data, name)
        if getattr(prop, name) != new_value:
            changed[name] = new_value
            setattr(prop, name, new_value)

    if prop.address_id != data.address_id:
        changed["address_id"] = data.address_id
        prop.address_id = data.address_id

    prop.full_clean(exclude=["cover_image", "slug", "reference_code"])
    prop.save()
    _sync_features(prop, data.feature_codes)

    if changed:
        _record(prop, action="property.updated", actor=actor, metadata={"changed": list(changed)})
    return prop


def _may_edit(actor, prop: Property) -> bool:
    if has_capability(actor, Capability.PROPERTY_EDIT_ANY):
        return True
    return has_capability(actor, Capability.PROPERTY_EDIT_OWN) and prop.agent_id == actor.pk


def _sync_features(prop: Property, codes: list[str]) -> None:
    if not codes:
        prop.features.clear()
        return
    prop.features.set(Feature.objects.filter(code__in=codes))


def _record(prop: Property, *, action: str, actor, metadata: dict) -> None:
    from apps.audit.services.recording import record_event

    record_event(actor=actor, action=action, target=prop, metadata=metadata)
