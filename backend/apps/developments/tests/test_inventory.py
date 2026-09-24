from decimal import Decimal

import pytest

from core.api.exceptions import ConflictError

from apps.developments.models import (
    Building,
    Development,
    Floor,
    Unit,
    UnitAvailability,
    UnitType,
)
from apps.developments.services.inventory import (
    link_listing,
    set_unit_availability,
    unlink_listing,
)
from apps.properties.models import AvailabilityStatus

pytestmark = pytest.mark.django_db


@pytest.fixture
def unit(address, staff):
    development = Development.objects.create(
        name="Green Park", slug="green-park", address=address, manager=staff
    )
    building = Building.objects.create(development=development, name="Building A")
    floor = Floor.objects.create(building=building, level=3, unit_count=4)
    unit_type = UnitType.objects.create(
        development=development, code="2R-54", name="Two rooms", rooms=2,
        usable_area=Decimal("54.00"),
    )
    return Unit.objects.create(floor=floor, unit_type=unit_type, number="3B")


def test_a_unit_inherits_its_type_characteristics(unit):
    assert unit.effective_rooms == 2
    assert unit.effective_usable_area == Decimal("54.00")


def test_per_unit_values_override_the_type(unit):
    unit.rooms = 3
    assert unit.effective_rooms == 3


def test_selling_a_unit_propagates_to_its_listing(unit, make_property, staff):
    listing = make_property()
    link_listing(unit, listing, actor=staff)

    set_unit_availability(unit, availability=UnitAvailability.SOLD, actor=staff)

    listing.refresh_from_db()
    assert listing.availability_status == AvailabilityStatus.SOLD


def test_a_sold_unit_cannot_be_listed(unit, make_property, staff):
    set_unit_availability(unit, availability=UnitAvailability.SOLD, actor=staff)
    with pytest.raises(ConflictError):
        link_listing(unit, make_property(), actor=staff)


def test_one_listing_cannot_back_two_units(unit, make_property, staff):
    listing = make_property()
    link_listing(unit, listing, actor=staff)

    other = Unit.objects.create(floor=unit.floor, number="3C")
    with pytest.raises(ConflictError):
        link_listing(other, listing, actor=staff)


def test_unlinking_leaves_the_unit_intact(unit, make_property, staff):
    link_listing(unit, make_property(), actor=staff)
    unlink_listing(unit, actor=staff)
    unit.refresh_from_db()
    assert unit.listing_id is None
    assert unit.availability == UnitAvailability.AVAILABLE
