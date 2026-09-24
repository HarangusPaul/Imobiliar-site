"""Django Admin for properties - the internal CRUD fallback.

Usable, but not the product. Note that publication is exposed as an admin
action routed through the domain service, so even the fallback UI cannot skip
the transition rules.
"""

from __future__ import annotations

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from core.api.exceptions import DomainError

from apps.media.admin import PropertyMediaInline
from apps.properties.models import Feature, Property, PublicationStatus
from apps.properties.services.publishing import transition_publication


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "group", "is_filterable", "is_premium_filter", "sort_order")
    list_filter = ("group", "is_filterable", "is_premium_filter")
    search_fields = ("code", "name")
    ordering = ("group", "sort_order", "name")
    prepopulated_fields = {"code": ("name",)}
    readonly_fields = ("uuid", "created_at", "updated_at")


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "reference_code", "title", "property_type", "transaction_type",
        "publication_status", "availability_status", "price", "currency",
        "city", "agent", "published_at",
    )
    list_filter = (
        "publication_status", "availability_status", "transaction_type",
        "property_type", "currency", "is_featured", "address__city",
    )
    search_fields = ("reference_code", "title", "slug", "short_description", "address__street")
    autocomplete_fields = ("address", "agent", "cover_image")
    filter_horizontal = ("features",)
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    ordering = ("-updated_at",)
    list_select_related = ("address__city", "agent")
    inlines = [PropertyMediaInline]
    actions = ["publish_selected", "archive_selected"]

    readonly_fields = ("uuid", "reference_code", "published_at", "created_at", "updated_at",
                       "price_per_square_metre")

    fieldsets = (
        (None, {"fields": ("title", "slug", "reference_code", "short_description", "description")}),
        (_("Classification"), {"fields": ("property_type", "transaction_type", "features")}),
        (_("State"), {"fields": ("publication_status", "availability_status", "is_featured",
                                 "published_at")}),
        (_("Location"), {"fields": ("address",)}),
        (_("Price"), {"fields": ("price", "currency", "rent_period", "price_on_request",
                                 "price_per_square_metre")}),
        (_("Characteristics"), {"fields": ("rooms", "bathrooms", "usable_area", "total_area",
                                           "floor", "total_floors", "year_built")}),
        (_("Ownership"), {"fields": ("agent", "cover_image")}),
        (_("Audit"), {"fields": ("uuid", "created_at", "updated_at")}),
    )

    @admin.display(description=_("City"), ordering="address__city__name")
    def city(self, obj: Property) -> str:
        return obj.address.city.name

    @admin.action(description=_("Publish selected listings"))
    def publish_selected(self, request, queryset) -> None:
        self._transition(request, queryset, PublicationStatus.PUBLISHED)

    @admin.action(description=_("Archive selected listings"))
    def archive_selected(self, request, queryset) -> None:
        self._transition(request, queryset, PublicationStatus.ARCHIVED)

    def _transition(self, request, queryset, target: str) -> None:
        succeeded, failed = 0, []
        for prop in queryset:
            try:
                transition_publication(prop, target=target, actor=request.user)
                succeeded += 1
            except DomainError as exc:
                failed.append(f"{prop.reference_code}: {exc.message}")

        if succeeded:
            self.message_user(request, f"{succeeded} listing(s) moved to {target}.",
                              messages.SUCCESS)
        for problem in failed:
            self.message_user(request, problem, messages.WARNING)
