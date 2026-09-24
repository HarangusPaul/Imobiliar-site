"""Public-facing property serializers.

Two shapes, deliberately different:

* PropertyCardSerializer - the grid. Small, flat, and it never touches
  description, documents, layouts or the full gallery. A 24-item page must not
  become a 24-item media dump.
* PropertyDetailSerializer - one listing. Everything a detail page needs, with
  media fetched in one prefetch.

Field-level visibility (exact address, owner contact) is decided by
apps.subscriptions, which is why the detail serializer reads entitlements from
the request context instead of guessing.
"""

from __future__ import annotations

from rest_framework import serializers

from apps.properties.models import Property
from apps.subscriptions.models import Entitlement
from apps.subscriptions.selectors.entitlements import has_entitlement


class PropertyLocationSerializer(serializers.Serializer):
    """Only what the address is willing to expose publicly."""

    city = serializers.CharField(source="city.name")
    city_slug = serializers.CharField(source="city.slug")
    neighborhood = serializers.SerializerMethodField()
    label = serializers.CharField(source="public_label")

    def get_neighborhood(self, address) -> str | None:
        return address.neighborhood.name if address.neighborhood_id else None


class PropertyCardSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    location = PropertyLocationSerializer(source="address", read_only=True)
    cover_image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id",
            "slug",
            "title",
            "short_description",
            "property_type",
            "transaction_type",
            "availability_status",
            "price",
            "currency",
            "rent_period",
            "rooms",
            "bathrooms",
            "usable_area",
            "floor",
            "location",
            "cover_image",
            "is_featured",
            "published_at",
        ]
        read_only_fields = fields

    def get_price(self, prop: Property):
        return None if prop.price_on_request else prop.price

    def get_cover_image(self, prop: Property) -> dict | None:
        """One image, resolved through the storage contract."""
        if not prop.cover_image_id:
            return None
        from core.contracts.registry import storage_service

        return {
            "url": storage_service().url(prop.cover_image.file_key),
            "alt": prop.cover_image.alt_text,
        }


class PropertyDetailSerializer(PropertyCardSerializer):
    description = serializers.CharField(read_only=True)
    features = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    layouts = serializers.SerializerMethodField()
    exact_address = serializers.SerializerMethodField()

    class Meta(PropertyCardSerializer.Meta):
        fields = PropertyCardSerializer.Meta.fields + [
            "description",
            "total_area",
            "total_floors",
            "year_built",
            "features",
            "gallery",
            "documents",
            "layouts",
            "exact_address",
            "created_at",
        ]
        read_only_fields = fields

    def get_features(self, prop: Property) -> list[dict]:
        return [
            {"code": f.code, "name": f.name, "group": f.group} for f in prop.features.all()
        ]

    def get_gallery(self, prop: Property) -> list[dict]:
        from apps.media.selectors.assets import gallery_for

        return _serialize_media(gallery_for(prop))

    def get_layouts(self, prop: Property) -> list[dict]:
        from apps.media.selectors.assets import layouts_for

        return _serialize_media(layouts_for(prop))

    def get_documents(self, prop: Property) -> list[dict]:
        """Documents are entitlement-gated."""
        user = getattr(self.context.get("request"), "user", None)
        if not has_entitlement(user, Entitlement.FULL_DOCUMENTS):
            return []
        from apps.media.selectors.assets import documents_for

        return _serialize_media(documents_for(prop))

    def get_exact_address(self, prop: Property) -> str | None:
        address = prop.address
        if address.is_exact_public:
            return address.full_label
        user = getattr(self.context.get("request"), "user", None)
        if has_entitlement(user, Entitlement.SUBSCRIBER_ONLY_FIELDS):
            return address.full_label
        return None


def _serialize_media(assets) -> list[dict]:
    from core.contracts.registry import storage_service

    storage = storage_service()
    return [
        {
            "id": str(asset.uuid),
            "url": storage.url(asset.file_key),
            "alt": asset.alt_text,
            "title": asset.title,
            "category": asset.category,
            "content_type": asset.content_type,
        }
        for asset in assets
    ]
