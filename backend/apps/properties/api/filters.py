"""Translate query parameters into a PropertySearchQuery.

Parsing lives at the API edge; the meaning of each filter lives in the
selector. This keeps querystring handling out of the domain and domain logic
out of the view.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from rest_framework.request import Request

from apps.properties.selectors.search import DEFAULT_SORT, SORT_OPTIONS, PropertySearchQuery

MAX_MULTI_VALUES = 20


def _decimal(params, key: str) -> Decimal | None:
    raw = params.get(key)
    if not raw:
        return None
    try:
        value = Decimal(raw)
    except (InvalidOperation, ValueError):
        return None
    return value if value >= 0 else None


def _int(params, key: str) -> int | None:
    raw = params.get(key)
    try:
        return int(raw) if raw not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _list(params, key: str) -> list[str]:
    """Accepts repeated params and comma-separated values, capped."""
    values: list[str] = []
    for raw in params.getlist(key):
        values.extend(part.strip() for part in raw.split(",") if part.strip())
    return values[:MAX_MULTI_VALUES]


def build_search_query(request: Request) -> PropertySearchQuery:
    params = request.query_params
    sort = params.get("sort", DEFAULT_SORT)
    return PropertySearchQuery(
        text=params.get("q", "").strip()[:120],
        transaction_type=params.get("transaction_type", ""),
        property_types=_list(params, "property_type"),
        city_slug=params.get("city", ""),
        neighborhood_slugs=_list(params, "neighborhood"),
        price_min=_decimal(params, "price_min"),
        price_max=_decimal(params, "price_max"),
        currency=params.get("currency", ""),
        rooms_min=_int(params, "rooms_min"),
        rooms_max=_int(params, "rooms_max"),
        area_min=_decimal(params, "area_min"),
        area_max=_decimal(params, "area_max"),
        floor_min=_int(params, "floor_min"),
        floor_max=_int(params, "floor_max"),
        year_built_min=_int(params, "year_built_min"),
        feature_codes=_list(params, "features"),
        only_featured=params.get("featured") == "true",
        sort=sort if sort in SORT_OPTIONS else DEFAULT_SORT,
    )
