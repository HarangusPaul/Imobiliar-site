"""Read-side queries for geography.

Used to build the public search facets. Counting published listings per city
is a locations query on purpose: it keeps the join in one reviewable place.
"""

from __future__ import annotations

from django.db.models import Count, Q, QuerySet

from apps.locations.models import City, Country, Neighborhood


def active_countries() -> QuerySet[Country]:
    return Country.objects.filter(is_active=True).order_by("name")


def cities_for(country_code: str | None = None) -> QuerySet[City]:
    queryset = City.objects.select_related("country")
    if country_code:
        queryset = queryset.filter(country__code=country_code.upper())
    return queryset.order_by("name")


def featured_cities() -> QuerySet[City]:
    return City.objects.filter(is_featured=True).order_by("name")


def neighborhoods_for(city_slug: str) -> QuerySet[Neighborhood]:
    return Neighborhood.objects.filter(city__slug=city_slug).order_by("name")


def cities_with_published_counts() -> QuerySet[City]:
    """City facets for the public search sidebar.

    The filter mirrors the public visibility rule in apps.properties. It is
    expressed as a Q here rather than imported, so locations stays free of a
    dependency on the properties domain.
    """
    return (
        City.objects.annotate(
            published_count=Count(
                "addresses__properties",
                filter=Q(addresses__properties__publication_status="published"),
                distinct=True,
            )
        )
        .filter(published_count__gt=0)
        .order_by("-published_count", "name")
    )
