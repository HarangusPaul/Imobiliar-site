"""Media write workflows.

The division of labour with services/storage is strict:

  this module                       the storage contract
  ----------------------------------------------------------------
  decides a file is a gallery       writes the bytes
  image for property 42
  validates the kind and size       returns an opaque key
  assigns alt text and order        can read the bytes back
  keeps the cover pointer true      deletes the bytes

No filesystem call appears anywhere in this app.
"""

from __future__ import annotations

from typing import BinaryIO

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Max

from core.api.exceptions import DomainError
from core.contracts.registry import storage_service

from apps.media.models import MediaAsset, MediaCategory, MediaKind

MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_DOCUMENT_BYTES = 25 * 1024 * 1024

ALLOWED_IMAGE_TYPES = frozenset({"image/jpeg", "image/png", "image/webp", "image/avif"})
ALLOWED_DOCUMENT_TYPES = frozenset(
    {"application/pdf", "image/jpeg", "image/png",
     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
)

#: Which storage namespace each category is filed under.
_NAMESPACES = {
    MediaCategory.GALLERY: "gallery",
    MediaCategory.COVER: "gallery",
    MediaCategory.LAYOUT: "layouts",
    MediaCategory.FLOOR_PLAN: "layouts",
    MediaCategory.SITE_PLAN: "layouts",
    MediaCategory.DOCUMENT: "documents",
    MediaCategory.CERTIFICATE: "documents",
    MediaCategory.VIDEO_THUMBNAIL: "thumbnails",
}


class UnsupportedMediaTypeError(DomainError):
    code = "unsupported_media_type"
    message = "This file type is not accepted."


class MediaTooLargeError(DomainError):
    code = "media_too_large"
    message = "This file is larger than the limit for its category."


def _kind_for(category: str) -> str:
    return (
        MediaKind.DOCUMENT
        if category in {MediaCategory.DOCUMENT, MediaCategory.CERTIFICATE}
        else MediaKind.IMAGE
    )


def _validate(kind: str, content_type: str, size_hint: int) -> None:
    allowed = ALLOWED_IMAGE_TYPES if kind == MediaKind.IMAGE else ALLOWED_DOCUMENT_TYPES
    if content_type not in allowed:
        raise UnsupportedMediaTypeError(
            f"{content_type} is not accepted for this category.",
            details={"allowed": sorted(allowed)},
        )
    limit = MAX_IMAGE_BYTES if kind == MediaKind.IMAGE else MAX_DOCUMENT_BYTES
    if size_hint > limit:
        raise MediaTooLargeError(details={"limit_bytes": limit, "size_bytes": size_hint})


@transaction.atomic
def attach_file(
    *,
    owner,
    stream: BinaryIO,
    filename: str,
    content_type: str,
    category: str = MediaCategory.GALLERY,
    size_hint: int = 0,
    title: str = "",
    alt_text: str = "",
    is_public: bool = True,
    uploaded_by=None,
) -> MediaAsset:
    """Store a file and record what it is and what it belongs to."""
    kind = _kind_for(category)
    _validate(kind, content_type, size_hint)

    namespace = f"{owner._meta.app_label}/{_NAMESPACES.get(category, 'misc')}"
    stored = storage_service().save(
        namespace=namespace, filename=filename, stream=stream, content_type=content_type
    )

    asset = MediaAsset.objects.create(
        file_key=stored.key,
        original_filename=filename,
        content_type=stored.content_type,
        kind=kind,
        category=category,
        size_bytes=stored.size,
        checksum=stored.checksum,
        title=title,
        alt_text=alt_text,
        is_public=is_public,
        sort_order=_next_sort_order(owner, category),
        content_type_ref=ContentType.objects.get_for_model(owner.__class__),
        object_id=owner.pk,
        uploaded_by=uploaded_by,
    )

    _maybe_set_cover(owner, asset)
    return asset


def _next_sort_order(owner, category: str) -> int:
    current = (
        MediaAsset.objects.for_object(owner)
        .filter(category=category)
        .aggregate(Max("sort_order"))["sort_order__max"]
    )
    return (current or 0) + 1


def _maybe_set_cover(owner, asset: MediaAsset) -> None:
    """Give an owner a cover image the first time one becomes available.

    Knowing that properties and developments have a cover_image field is a
    media-domain concern: this app owns the relation between an entity and its
    imagery.
    """
    if asset.category not in {MediaCategory.GALLERY, MediaCategory.COVER}:
        return
    if not hasattr(owner, "cover_image_id") or owner.cover_image_id:
        return
    owner.cover_image = asset
    owner.save(update_fields=["cover_image", "updated_at"])


@transaction.atomic
def reorder(owner, *, asset_uuids: list[str]) -> None:
    """Apply an explicit order coming from the dashboard gallery editor."""
    assets = {str(a.uuid): a for a in MediaAsset.objects.for_object(owner)}
    for position, uuid in enumerate(asset_uuids, start=1):
        asset = assets.get(uuid)
        if asset and asset.sort_order != position:
            asset.sort_order = position
            asset.save(update_fields=["sort_order", "updated_at"])


@transaction.atomic
def detach(asset: MediaAsset, *, purge_file: bool = False) -> None:
    """Soft-delete the metadata, optionally discarding the bytes.

    The default keeps the file: a media row removed by mistake is recoverable,
    and storage is cheap compared with losing a property gallery.
    """
    owner = asset.owner
    if owner is not None and getattr(owner, "cover_image_id", None) == asset.pk:
        replacement = (
            MediaAsset.objects.for_object(owner)
            .exclude(pk=asset.pk)
            .in_category(MediaCategory.GALLERY, MediaCategory.COVER)
            .order_by("sort_order")
            .first()
        )
        owner.cover_image = replacement
        owner.save(update_fields=["cover_image", "updated_at"])

    asset.soft_delete()
    if purge_file:
        transaction.on_commit(lambda: storage_service().delete(asset.file_key))
