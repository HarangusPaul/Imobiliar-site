from __future__ import annotations

from django.contrib import admin

from apps.locations.models import Address, City, Country, Neighborhood


class NeighborhoodInline(admin.TabularInline):
    model = Neighborhood
    extra = 0
    prepopulated_fields = {"slug": ("name",)}
    fields = ("name", "slug", "latitude", "longitude")


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "phone_prefix", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("name",)
    readonly_fields = ("uuid", "created_at", "updated_at")


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "county", "country", "is_featured", "neighborhood_count")
    list_filter = ("country", "is_featured")
    search_fields = ("name", "county", "slug")
    autocomplete_fields = ("country",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)
    inlines = [NeighborhoodInline]
    readonly_fields = ("uuid", "created_at", "updated_at")

    @admin.display(description="Neighborhoods")
    def neighborhood_count(self, obj: City) -> int:
        return obj.neighborhoods.count()


@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ("name", "city")
    list_filter = ("city__country", "city")
    search_fields = ("name", "slug", "city__name")
    autocomplete_fields = ("city",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("city__name", "name")
    readonly_fields = ("uuid", "created_at", "updated_at")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("full_label", "city", "neighborhood", "is_exact_public")
    list_filter = ("is_exact_public", "city")
    search_fields = ("street", "street_number", "postal_code", "city__name", "neighborhood__name")
    autocomplete_fields = ("city", "neighborhood")
    ordering = ("city__name", "street")
    readonly_fields = ("uuid", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("city", "neighborhood", "street", "street_number",
                           "building_identifier", "postal_code")}),
        ("Map", {"fields": ("latitude", "longitude")}),
        ("Visibility", {"fields": ("is_exact_public",)}),
        ("Audit", {"fields": ("uuid", "created_at", "updated_at")}),
    )
