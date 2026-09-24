"""Write workflows for development inventory.

The rule this module protects: a unit's availability and its listing must stay
consistent. Selling a unit withdraws its public listing; publishing inventory
must not resurrect a sold apartment.
"""

from __future__ import annotations

from django.db import transaction

from core.api.exceptions import ConflictError

from apps.developments.models import Unit, UnitAvailability
from apps.properties.models import AvailabilityStatus, Property

#: How unit inventory state maps onto listing availability.
_UNIT_TO_LISTING = {
    UnitAvailability.AVAILABLE: AvailabilityStatus.AVAILABLE,
    UnitAvailability.RESERVED: AvailabilityStatus.RESERVED,
    UnitAvailability.SOLD: AvailabilityStatus.SOLD,
    UnitAvailability.RENTED: AvailabilityStatus.RENTED,
    UnitAvailability.NOT_FOR_SALE: AvailabilityStatus.UNAVAILABLE,
}


@transaction.atomic
def set_unit_availability(unit: Unit, *, availability: str, actor) -> Unit:
    """Change inventory state and propagate it to the listing, if any."""
    previous = unit.availability
    if previous == availability:
        return unit

    unit.availability = availability
    unit.save(update_fields=["availability", "updated_at"])

    if unit.listing_id:
        listing = unit.listing
        listing.availability_status = _UNIT_TO_LISTING[availability]
        listing.save(update_fields=["availability_status", "updated_at"])

    _record(unit, action="unit.availability_changed", actor=actor,
            metadata={"from": previous, "to": availability})
    return unit


@transaction.atomic
def link_listing(unit: Unit, listing: Property, *, actor) -> Unit:
    """Attach a public listing to a unit.

    One listing per unit is enforced by the OneToOne; this adds the domain
    checks the database cannot express.
    """
    if unit.listing_id and unit.listing_id != listing.pk:
        raise ConflictError("This unit already has a listing. Unlink it first.")
    if unit.availability in {UnitAvailability.SOLD, UnitAvailability.NOT_FOR_SALE}:
        raise ConflictError("A sold or withheld unit cannot be listed publicly.")
    if Unit.objects.filter(listing=listing).exclude(pk=unit.pk).exists():
        raise ConflictError("That listing is already attached to another unit.")

    unit.listing = listing
    unit.save(update_fields=["listing", "updated_at"])

    _record(unit, action="unit.listing_linked", actor=actor,
            metadata={"listing": str(listing.uuid), "reference_code": listing.reference_code})
    return unit


@transaction.atomic
def unlink_listing(unit: Unit, *, actor) -> Unit:
    if not unit.listing_id:
        return unit
    previous = str(unit.listing.uuid)
    unit.listing = None
    unit.save(update_fields=["listing", "updated_at"])

    _record(unit, action="unit.listing_unlinked", actor=actor, metadata={"listing": previous})
    return unit


def _record(unit: Unit, *, action: str, actor, metadata: dict) -> None:
    from apps.audit.services.recording import record_event

    record_event(actor=actor, action=action, target=unit, metadata=metadata)
