"""Property search and filtering.

This is the single owner of listing query logic. It is not a service, because
searching reads and never writes; it is not in `services/`, because it is
real-estate business logic and would be meaningless to any other project.

The subscription seam matters here: which filters a caller may use is an
entitlement question, so this module asks apps.subscriptions rather than
deciding for itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from django.db.models import Q, QuerySet

from core.validation import clamp_int

from apps.properties.models import Feature, Property
from apps.subscriptions.selectors.entitlements import can_use_premium_filters

#: Orderings a caller may request, mapped to real ordering tuples so a client
#: can never inject an arbitrary column.
SORT_OPTIONS: dict[str, tuple[str, ...]] = {
    "newest": ("-published_at", "-id"),
    "price_asc": ("price", "-id"),
    "price_desc": ("-price", "-id"),
    "area_desc": ("-usable_area", "-id"),
    "featured": ("-is_featured", "-published_at", "-id"),
}
DEFAULT_SORT = "newest"


@dataclass(slots=True)
class PropertySearchQuery:
    """A validated, already-parsed search request."""

    text: str = ""
    transaction_type: str = ""
    property_types: list[str] = field(default_factory=list)
    city_slug: str = ""
    neighborhood_slugs: list[str] = field(default_factory=list)
    price_min: Decimal | None = None
    price_max: Decimal | None = None
    currency: str = ""
    rooms_min: int | None = None
    rooms_max: int | None = None
    area_min: Decimal | None = None
    area_max: Decimal | None = None
    floor_min: int | None = None
    floor_max: int | None = None
    year_built_min: int | None = None
    feature_codes: list[str] = field(default_factory=list)
    only_featured: bool = False
    sort: str = DEFAULT_SORT


def search_published(query: PropertySearchQuery, *, user=None) -> QuerySet[Property]:
    """Public listing search.

    Always starts from `published()`, so no filter combination can widen
    visibility beyond what the public is allowed to see.
    """
    queryset = Property.objects.published().for_card()
    queryset = _apply_filters(queryset, query, user=user)
    return queryset.order_by(*SORT_OPTIONS.get(query.sort, SORT_OPTIONS[DEFAULT_SORT]))


def _apply_filters(
    queryset: QuerySet[Property], query: PropertySearchQuery, *, user=None
) -> QuerySet[Property]:
    if query.text:
        queryset = queryset.filter(
            Q(title__icontains=query.text)
            | Q(short_description__icontains=query.text)
            | Q(reference_code__iexact=query.text)
        )

    if query.transaction_type:
        queryset = queryset.filter(transaction_type=query.transaction_type)
    if query.property_types:
        queryset = queryset.filter(property_type__in=query.property_types)

    if query.city_slug:
        queryset = queryset.filter(address__city__slug=query.city_slug)
    if query.neighborhood_slugs:
        queryset = queryset.filter(address__neighborhood__slug__in=query.neighborhood_slugs)

    if query.currency:
        queryset = queryset.filter(currency=query.currency)
    if query.price_min is not None:
        queryset = queryset.filter(price__gte=query.price_min)
    if query.price_max is not None:
        queryset = queryset.filter(price__lte=query.price_max)

    if query.rooms_min is not None:
        queryset = queryset.filter(rooms__gte=query.rooms_min)
    if query.rooms_max is not None:
        queryset = queryset.filter(rooms__lte=query.rooms_max)

    if query.area_min is not None:
        queryset = queryset.filter(usable_area__gte=query.area_min)
    if query.area_max is not None:
        queryset = queryset.filter(usable_area__lte=query.area_max)

    if query.floor_min is not None:
        queryset = queryset.filter(floor__gte=query.floor_min)
    if query.floor_max is not None:
        queryset = queryset.filter(floor__lte=query.floor_max)

    if query.year_built_min is not None:
        queryset = queryset.filter(year_built__gte=query.year_built_min)

    if query.only_featured:
        queryset = queryset.filter(is_featured=True)

    if query.feature_codes:
        queryset = _apply_feature_filters(queryset, query.feature_codes, user=user)

    return queryset


def _apply_feature_filters(
    queryset: QuerySet[Property], codes: list[str], *, user=None
) -> QuerySet[Property]:
    """Filter by amenities, dropping premium facets the caller has not bought.

    Silently ignoring an unentitled filter (rather than erroring) keeps a
    shared or bookmarked search URL working for every visitor; they simply see
    a broader result set.
    """
    allowed = set(
        Feature.objects.filter(code__in=codes, is_filterable=True).values_list("code", flat=True)
    )
    if not can_use_premium_filters(user):
        premium = set(
            Feature.objects.filter(code__in=allowed, is_premium_filter=True).values_list(
                "code", flat=True
            )
        )
        allowed -= premium

    for code in allowed:
        # Chained filters, not `__in`: features must all be present, not any.
        queryset = queryset.filter(features__code=code)
    return queryset.distinct() if allowed else queryset


def get_published_by_slug(slug: str) -> Property | None:
    return Property.objects.published().for_detail().filter(slug=slug).first()


def featured_published(limit: int = 8) -> QuerySet[Property]:
    limit = clamp_int(limit, minimum=1, maximum=24, default=8)
    return (
        Property.objects.published()
        .for_card()
        .filter(is_featured=True)
        .order_by("-published_at")[:limit]
    )


def similar_to(prop: Property, limit: int = 4) -> QuerySet[Property]:
    """Same city, same transaction type, comparable price band."""
    low, high = prop.price * Decimal("0.75"), prop.price * Decimal("1.25")
    return (
        Property.objects.published()
        .for_card()
        .filter(
            address__city_id=prop.address.city_id,
            transaction_type=prop.transaction_type,
            price__gte=low,
            price__lte=high,
        )
        .exclude(pk=prop.pk)
        .order_by("-is_featured", "-published_at")[: clamp_int(limit, minimum=1, maximum=12, default=4)]
    )
