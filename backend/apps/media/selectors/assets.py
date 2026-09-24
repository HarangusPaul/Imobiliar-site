"""Read-side queries for media.

Every consumer goes through these helpers, so the public/internal split and
the ordering rule are applied in one place.
"""

from __future__ import annotations

from django.db.models import QuerySet

from apps.media.models import MediaAsset, MediaCategory


def for_owner(instance, *, public_only: bool = True) -> QuerySet[MediaAsset]:
    queryset = MediaAsset.objects.for_object(instance)
    return queryset.public() if public_only else queryset


def gallery_for(instance, *, public_only: bool = True) -> QuerySet[MediaAsset]:
    return for_owner(instance, public_only=public_only).in_category(
        MediaCategory.GALLERY, MediaCategory.COVER
    ).order_by("sort_order", "created_at")


def layouts_for(instance, *, public_only: bool = True) -> QuerySet[MediaAsset]:
    return for_owner(instance, public_only=public_only).in_category(
        MediaCategory.LAYOUT, MediaCategory.FLOOR_PLAN, MediaCategory.SITE_PLAN
    ).order_by("sort_order")


def documents_for(instance, *, public_only: bool = False) -> QuerySet[MediaAsset]:
    """Documents default to internal.

    Whether a visitor may see them is an entitlement question answered by the
    caller (see the property detail serializer), not a default of this app.
    """
    return for_owner(instance, public_only=public_only).in_category(
        MediaCategory.DOCUMENT, MediaCategory.CERTIFICATE
    ).order_by("sort_order")


def first_gallery_image(instance) -> MediaAsset | None:
    return gallery_for(instance).first()
