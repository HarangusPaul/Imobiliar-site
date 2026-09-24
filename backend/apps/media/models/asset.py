"""Media metadata.

This app owns what a file *means*: its category, its alt text, its position in
a gallery, and what it is attached to. It does not own bytes. The column
file_key holds an opaque handle returned by the storage contract, and the file
itself lives wherever the configured implementation put it.

Binary content is never stored in PostgreSQL.

Attachment is generic (content type + object id) rather than a foreign key per
owner, because media attaches to properties, developments, buildings, floors,
unit types and content pages, and that list will grow. A per-owner join table
for each would multiply without adding meaning.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel, SoftDeleteModel


class MediaCategory(models.TextChoices):
    """What role a file plays. Drives which API surface exposes it."""

    GALLERY = "gallery", _("Gallery image")
    COVER = "cover", _("Cover image")
    LAYOUT = "layout", _("Apartment layout")
    FLOOR_PLAN = "floor_plan", _("Building floor plan")
    SITE_PLAN = "site_plan", _("Site plan")
    DOCUMENT = "document", _("Document")
    CERTIFICATE = "certificate", _("Energy or legal certificate")
    VIDEO_THUMBNAIL = "video_thumbnail", _("Video thumbnail")


class MediaKind(models.TextChoices):
    IMAGE = "image", _("Image")
    DOCUMENT = "document", _("Document")


#: Categories a visitor may see without any entitlement.
PUBLIC_CATEGORIES = frozenset(
    {
        MediaCategory.GALLERY,
        MediaCategory.COVER,
        MediaCategory.LAYOUT,
        MediaCategory.FLOOR_PLAN,
        MediaCategory.SITE_PLAN,
        MediaCategory.VIDEO_THUMBNAIL,
    }
)


class MediaAssetQuerySet(models.QuerySet):
    def for_object(self, instance) -> "MediaAssetQuerySet":
        return self.filter(
            content_type_ref=ContentType.objects.get_for_model(instance.__class__),
            object_id=instance.pk,
        )

    def public(self) -> "MediaAssetQuerySet":
        return self.filter(is_public=True, category__in=PUBLIC_CATEGORIES)

    def in_category(self, *categories: str) -> "MediaAssetQuerySet":
        return self.filter(category__in=categories)


class MediaAsset(BaseModel, SoftDeleteModel):
    file_key = models.CharField(
        max_length=500,
        unique=True,
        help_text=_("Opaque handle returned by the storage contract. Never a local path."),
    )
    original_filename = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=100)
    kind = models.CharField(max_length=16, choices=MediaKind.choices, default=MediaKind.IMAGE)
    category = models.CharField(
        max_length=20, choices=MediaCategory.choices, default=MediaCategory.GALLERY, db_index=True
    )

    size_bytes = models.PositiveBigIntegerField(default=0)
    checksum = models.CharField(max_length=64, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)

    title = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(
        max_length=255, blank=True, help_text=_("Describes the image for screen readers and SEO.")
    )
    sort_order = models.PositiveSmallIntegerField(default=0, db_index=True)
    is_public = models.BooleanField(
        default=True, help_text=_("False keeps the file internal to the dashboard.")
    )

    content_type_ref = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="media_assets", db_column="content_type_id"
    )
    object_id = models.PositiveBigIntegerField()
    owner = GenericForeignKey("content_type_ref", "object_id")

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="uploaded_media",
    )

    objects = MediaAssetQuerySet.as_manager()
    all_objects = models.Manager.from_queryset(MediaAssetQuerySet)()

    class Meta:
        verbose_name = _("media asset")
        verbose_name_plural = _("media assets")
        ordering = ["sort_order", "created_at"]
        indexes = [
            models.Index(
                fields=["content_type_ref", "object_id", "category", "sort_order"],
                name="media_owner_category_idx",
            )
        ]

    def __str__(self) -> str:
        return self.title or self.original_filename or self.file_key

    @property
    def url(self) -> str:
        """Resolved through the contract, never constructed here."""
        from core.contracts.registry import storage_service

        return storage_service().url(self.file_key)
