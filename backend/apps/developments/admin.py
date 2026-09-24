"""Django Admin for developments.

Inlines follow the hierarchy one level at a time: buildings inside a
development, floors inside a building, units inside a floor. Nesting further
would be unusable in the default admin.
"""

from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.media.admin import DevelopmentMediaInline
from apps.developments.models import Building, Development, Floor, Unit, UnitType


class BuildingInline(admin.TabularInline):
    model = Building
    extra = 0
    fields = ("name", "code", "status", "floors_above_ground", "estimated_completion", "sort_order")
    show_change_link = True


class UnitTypeInline(admin.TabularInline):
    model = UnitType
    extra = 0
    fields = ("code", "name", "rooms", "bathrooms", "usable_area", "layout")
    autocomplete_fields = ("layout",)
    show_change_link = True


class FloorInline(admin.TabularInline):
    model = Floor
    extra = 0
    fields = ("level", "name", "unit_count", "floor_plan")
    autocomplete_fields = ("floor_plan",)
    ordering = ("level",)
    show_change_link = True


class UnitInline(admin.TabularInline):
    model = Unit
    extra = 0
    fields = ("number", "unit_type", "availability", "rooms", "usable_area", "price", "listing")
    autocomplete_fields = ("unit_type", "listing")
    ordering = ("number",)
    show_change_link = True


@admin.register(Development)
class DevelopmentAdmin(admin.ModelAdmin):
    list_display = ("name", "developer_name", "status", "publication_status", "city",
                    "building_count", "estimated_completion", "is_featured")
    list_filter = ("publication_status", "status", "is_featured", "address__city")
    search_fields = ("name", "slug", "developer_name", "short_description")
    autocomplete_fields = ("address", "manager", "cover_image")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-is_featured", "name")
    inlines = [BuildingInline, UnitTypeInline, DevelopmentMediaInline]
    readonly_fields = ("uuid", "created_at", "updated_at", "published_at")

    @admin.display(description=_("City"))
    def city(self, obj: Development) -> str:
        return obj.address.city.name

    @admin.display(description=_("Buildings"))
    def building_count(self, obj: Development) -> int:
        return obj.buildings.count()


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("name", "development", "status", "floors_above_ground", "floor_count")
    list_filter = ("status", "development")
    search_fields = ("name", "code", "development__name")
    autocomplete_fields = ("development", "address")
    ordering = ("development__name", "sort_order")
    inlines = [FloorInline]
    readonly_fields = ("uuid", "created_at", "updated_at")

    @admin.display(description=_("Floors"))
    def floor_count(self, obj: Building) -> int:
        return obj.floors.count()


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ("__str__", "level", "unit_count", "available_units")
    list_filter = ("building__development", "building")
    search_fields = ("building__name", "building__development__name", "name")
    autocomplete_fields = ("building", "floor_plan")
    ordering = ("building", "level")
    inlines = [UnitInline]
    readonly_fields = ("uuid", "created_at", "updated_at")

    @admin.display(description=_("Available"))
    def available_units(self, obj: Floor) -> int:
        return obj.units.available().count()


@admin.register(UnitType)
class UnitTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "development", "rooms", "bathrooms", "usable_area")
    list_filter = ("development", "rooms")
    search_fields = ("code", "name", "development__name")
    autocomplete_fields = ("development", "layout")
    ordering = ("development__name", "rooms")
    readonly_fields = ("uuid", "created_at", "updated_at")


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("number", "floor", "unit_type", "availability", "price", "currency", "listing")
    list_filter = ("availability", "floor__building__development", "floor__building")
    search_fields = ("number", "floor__building__name", "floor__building__development__name")
    autocomplete_fields = ("floor", "unit_type", "listing")
    ordering = ("floor", "number")
    list_select_related = ("floor__building", "unit_type", "listing")
    readonly_fields = ("uuid", "created_at", "updated_at")
