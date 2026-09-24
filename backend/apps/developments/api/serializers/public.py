"""Public development serializers.

Same discipline as properties: the list is a card, the detail is the full
structure. A project page returns its buildings, floors and available units in
one response because that is one navigational unit for the visitor - but it
still never inlines every document or the full gallery of every unit.
"""

from __future__ import annotations

from rest_framework import serializers

from apps.developments.models import Building, Development, Floor, Unit, UnitType


class DevelopmentCardSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    city = serializers.CharField(source="address.city.name", read_only=True)
    location = serializers.CharField(source="address.public_label", read_only=True)
    cover_image = serializers.SerializerMethodField()
    available_units = serializers.IntegerField(read_only=True, default=0)
    price_from = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True, allow_null=True
    )

    class Meta:
        model = Development
        fields = [
            "id",
            "slug",
            "name",
            "short_description",
            "developer_name",
            "status",
            "city",
            "location",
            "estimated_completion",
            "cover_image",
            "available_units",
            "price_from",
            "is_featured",
        ]
        read_only_fields = fields

    def get_cover_image(self, development: Development) -> dict | None:
        if not development.cover_image_id:
            return None
        from core.contracts.registry import storage_service

        return {
            "url": storage_service().url(development.cover_image.file_key),
            "alt": development.cover_image.alt_text,
        }


class UnitSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    rooms = serializers.IntegerField(source="effective_rooms", read_only=True)
    usable_area = serializers.DecimalField(
        source="effective_usable_area", max_digits=8, decimal_places=2, read_only=True
    )
    listing_slug = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = [
            "id",
            "number",
            "availability",
            "rooms",
            "usable_area",
            "orientation",
            "price",
            "currency",
            "listing_slug",
        ]
        read_only_fields = fields

    def get_listing_slug(self, unit: Unit) -> str | None:
        """Only surfaces a link when the listing is actually public."""
        return unit.listing.slug if unit.is_publicly_listed else None


class FloorSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    units = UnitSerializer(many=True, read_only=True)
    floor_plan = serializers.SerializerMethodField()

    class Meta:
        model = Floor
        fields = ["id", "level", "name", "unit_count", "floor_plan", "units"]
        read_only_fields = fields

    def get_floor_plan(self, floor: Floor) -> str | None:
        if not floor.floor_plan_id:
            return None
        from core.contracts.registry import storage_service

        return storage_service().url(floor.floor_plan.file_key)


class BuildingSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    floors = FloorSerializer(many=True, read_only=True)

    class Meta:
        model = Building
        fields = [
            "id",
            "name",
            "code",
            "status",
            "floors_above_ground",
            "floors_below_ground",
            "estimated_completion",
            "floors",
        ]
        read_only_fields = fields


class UnitTypeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    layout = serializers.SerializerMethodField()

    class Meta:
        model = UnitType
        fields = [
            "id",
            "code",
            "name",
            "rooms",
            "bathrooms",
            "usable_area",
            "built_area",
            "balcony_area",
            "layout",
        ]
        read_only_fields = fields

    def get_layout(self, unit_type: UnitType) -> str | None:
        if not unit_type.layout_id:
            return None
        from core.contracts.registry import storage_service

        return storage_service().url(unit_type.layout.file_key)


class DevelopmentDetailSerializer(DevelopmentCardSerializer):
    description = serializers.CharField(read_only=True)
    buildings = BuildingSerializer(many=True, read_only=True)
    unit_types = UnitTypeSerializer(many=True, read_only=True)
    availability_summary = serializers.DictField(read_only=True)

    class Meta(DevelopmentCardSerializer.Meta):
        fields = DevelopmentCardSerializer.Meta.fields + [
            "description",
            "buildings",
            "unit_types",
            "availability_summary",
        ]
        read_only_fields = fields
