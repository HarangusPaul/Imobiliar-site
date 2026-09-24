"""Django Admin for media.

The generic inline lets staff manage a gallery from the property or
development page, which is where they actually think about it.
"""

from __future__ import annotations

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.media.models import MediaAsset


class MediaAssetInline(GenericTabularInline):
    model = MediaAsset
    ct_field = "content_type_ref"
    ct_fk_field = "object_id"
    extra = 0
    fields = ("preview", "category", "title", "alt_text", "sort_order", "is_public")
    readonly_fields = ("preview",)
    ordering = ("sort_order",)

    @admin.display(description=_("Preview"))
    def preview(self, obj: MediaAsset) -> str:
        if not obj.pk or obj.kind != "image":
            return "-"
        return format_html('<img src="{}" style="max-height:60px;" alt="" />', obj.url)


class PropertyMediaInline(MediaAssetInline):
    """Named alias used by the property admin."""

    verbose_name = _("media item")
    verbose_name_plural = _("media items")


class DevelopmentMediaInline(MediaAssetInline):
    verbose_name = _("media item")
    verbose_name_plural = _("media items")


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("__str__", "category", "kind", "owner_label", "sort_order", "is_public",
                    "size_kb", "created_at")
    list_filter = ("category", "kind", "is_public", "content_type_ref")
    search_fields = ("title", "alt_text", "original_filename", "file_key")
    autocomplete_fields = ("uploaded_by",)
    ordering = ("-created_at",)
    readonly_fields = ("uuid", "file_key", "content_type", "size_bytes", "checksum",
                       "width", "height", "preview", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("preview", "category", "kind", "title", "alt_text", "sort_order",
                           "is_public")}),
        (_("Attachment"), {"fields": ("content_type_ref", "object_id", "uploaded_by")}),
        (_("Stored file"), {"fields": ("file_key", "original_filename", "content_type",
                                       "size_bytes", "checksum", "width", "height")}),
        (_("Audit"), {"fields": ("uuid", "created_at", "updated_at")}),
    )

    @admin.display(description=_("Attached to"))
    def owner_label(self, obj: MediaAsset) -> str:
        return str(obj.owner) if obj.owner else "-"

    @admin.display(description=_("Size"), ordering="size_bytes")
    def size_kb(self, obj: MediaAsset) -> str:
        return f"{obj.size_bytes / 1024:.0f} KB"

    @admin.display(description=_("Preview"))
    def preview(self, obj: MediaAsset) -> str:
        if not obj.pk or obj.kind != "image":
            return "-"
        return format_html('<img src="{}" style="max-height:200px;" alt="" />', obj.url)
