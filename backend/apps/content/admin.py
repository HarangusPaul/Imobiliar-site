from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.content.models import PresentationPage


@admin.register(PresentationPage)
class PresentationPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "sort_order", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("title", "slug", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("sort_order", "title")
    autocomplete_fields = ("og_image",)
    readonly_fields = ("uuid", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("title", "slug", "summary", "body", "is_published", "sort_order")}),
        (_("SEO"), {"fields": ("seo_title", "seo_description", "seo_keywords",
                               "og_image", "canonical_path", "noindex")}),
        (_("Audit"), {"fields": ("uuid", "created_at", "updated_at")}),
    )
