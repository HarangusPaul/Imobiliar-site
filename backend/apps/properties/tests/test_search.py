from decimal import Decimal

import pytest
from django.utils import timezone

from apps.properties.models import Property, PropertyType, PublicationStatus, TransactionType
from apps.properties.selectors.search import PropertySearchQuery, search_published

pytestmark = pytest.mark.django_db


def _publish(prop: Property) -> Property:
    """Bypass the service on purpose: these tests are about the read path."""
    prop.publication_status = PublicationStatus.PUBLISHED
    prop.published_at = timezone.now()
    prop.save(update_fields=["publication_status", "published_at"])
    return prop


def test_drafts_never_appear_in_public_search(make_property):
    make_property()
    assert search_published(PropertySearchQuery()).count() == 0


def test_published_listings_appear(make_property):
    _publish(make_property())
    assert search_published(PropertySearchQuery()).count() == 1


def test_price_and_type_filters_narrow_the_result(make_property):
    _publish(make_property(title="Cheap flat", price=Decimal("90000.00")))
    _publish(make_property(title="Pricey flat", price=Decimal("250000.00")))
    _publish(
        make_property(
            title="A house", price=Decimal("300000.00"), property_type=PropertyType.HOUSE
        )
    )

    results = search_published(PropertySearchQuery(price_max=Decimal("100000.00")))
    assert [p.title for p in results] == ["Cheap flat"]

    houses = search_published(PropertySearchQuery(property_types=[PropertyType.HOUSE]))
    assert [p.title for p in houses] == ["A house"]


def test_sort_is_restricted_to_known_options(make_property):
    _publish(make_property(title="A", price=Decimal("90000.00")))
    _publish(make_property(title="B", price=Decimal("80000.00")))

    ascending = search_published(PropertySearchQuery(sort="price_asc"))
    assert [p.title for p in ascending] == ["B", "A"]

    fallback = search_published(PropertySearchQuery(sort="; drop table"))
    assert fallback.count() == 2


def test_rentals_and_sales_do_not_mix(make_property):
    _publish(make_property(title="For sale"))
    _publish(
        make_property(
            title="For rent",
            transaction_type=TransactionType.RENT,
            rent_period="month",
            price=Decimal("500.00"),
        )
    )
    results = search_published(PropertySearchQuery(transaction_type=TransactionType.RENT))
    assert [p.title for p in results] == ["For rent"]
