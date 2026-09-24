"""Read-side queries for developments.

The public development page is a nested read: project, buildings, floors,
available units. Done naively that is one query per floor. These selectors
shape the prefetches so the whole page costs a fixed, small number of queries
regardless of how many buildings a project has.
"""

from __future__ import annotations

from django.db.models import Count, Min, Prefetch, Q, QuerySet

from apps.developments.models import Building, Development, Floor, Unit, UnitAvailability


def published_developments() -> QuerySet[Development]:
    """The public project list, annotated with the numbers the card shows."""
    return (
        Development.objects.published()
        .select_related("address__city", "cover_image")
        .annotate(
            available_units=Count(
                "buildings__floors__units",
                filter=Q(buildings__floors__units__availability=UnitAvailability.AVAILABLE),
                distinct=True,
            ),
            price_from=Min(
                "buildings__floors__units__price",
                filter=Q(buildings__floors__units__availability=UnitAvailability.AVAILABLE),
            ),
        )
        .order_by("-is_featured", "name")
    )


def get_published_by_slug(slug: str) -> Development | None:
    """One project with its full structure, in a bounded number of queries."""
    units = Unit.objects.select_related("unit_type", "listing").order_by("number")
    floors = Floor.objects.select_related("floor_plan").prefetch_related(
        Prefetch("units", queryset=units)
    ).order_by("level")
    buildings = Building.objects.prefetch_related(Prefetch("floors", queryset=floors)).order_by(
        "sort_order", "name"
    )

    return (
        Development.objects.published()
        .select_related("address__city", "address__neighborhood", "cover_image")
        .prefetch_related(Prefetch("buildings", queryset=buildings), "unit_types__layout")
        .filter(slug=slug)
        .first()
    )


def available_units_for(development: Development) -> QuerySet[Unit]:
    return (
        Unit.objects.filter(floor__building__development=development)
        .available()
        .select_related("unit_type", "floor__building", "listing")
        .order_by("floor__building__sort_order", "floor__level", "number")
    )


def unit_availability_summary(development: Development) -> dict[str, int]:
    """Counts per availability state, for the project header."""
    rows = (
        Unit.objects.filter(floor__building__development=development)
        .values("availability")
        .annotate(total=Count("id"))
    )
    return {row["availability"]: row["total"] for row in rows}
