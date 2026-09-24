"""Dashboard property serializers.

Distinct from the public ones on purpose. The dashboard sees internal state
(publication status, agent, audit timestamps) and writes; the public API sees
neither. Merging the two would mean one serializer deciding what to hide based
on the caller, which is exactly the pattern this architecture avoids.
"""

from __future__ import annotations

from rest_framework import serializers

from apps.properties.models import (
    AvailabilityStatus,
    Currency,
    Property,
    PropertyType,
    PublicationStatus,
    RentPeriod,
    TransactionType,
)


class DashboardPropertyListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    city = serializers.CharField(source="address.city.name", read_only=True)
    agent_name = serializers.CharField(source="agent.get_full_name", read_only=True)

    class Meta:
        model = Property
        fields = [
            "id",
            "reference_code",
            "title",
            "slug",
            "property_type",
            "transaction_type",
            "publication_status",
            "availability_status",
            "price",
            "currency",
            "city",
            "agent_name",
            "is_featured",
            "published_at",
            "updated_at",
        ]
        read_only_fields = fields


class DashboardPropertyWriteSerializer(serializers.Serializer):
    """Input validation only.

    Note what is absent: no publication_status, no slug, no reference_code.
    Those are outcomes of a service call, never client-supplied.
    """

    title = serializers.CharField(max_length=200)
    property_type = serializers.ChoiceField(choices=PropertyType.choices)
    transaction_type = serializers.ChoiceField(choices=TransactionType.choices)
    address_id = serializers.IntegerField()

    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.ChoiceField(choices=Currency.choices, default=Currency.EUR)
    rent_period = serializers.ChoiceField(
        choices=RentPeriod.choices, required=False, allow_blank=True, default=""
    )
    price_on_request = serializers.BooleanField(default=False)

    short_description = serializers.CharField(
        max_length=300, required=False, allow_blank=True, default=""
    )
    description = serializers.CharField(required=False, allow_blank=True, default="")

    rooms = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=100)
    bathrooms = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=50)
    usable_area = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False, allow_null=True
    )
    total_area = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    floor = serializers.IntegerField(required=False, allow_null=True, min_value=-10, max_value=200)
    total_floors = serializers.IntegerField(
        required=False, allow_null=True, min_value=0, max_value=200
    )
    year_built = serializers.IntegerField(
        required=False, allow_null=True, min_value=1700, max_value=2100
    )

    feature_codes = serializers.ListField(
        child=serializers.SlugField(), required=False, default=list
    )
    agent_id = serializers.IntegerField(required=False, allow_null=True)


class PublicationTransitionSerializer(serializers.Serializer):
    target = serializers.ChoiceField(choices=PublicationStatus.choices)


class AvailabilityTransitionSerializer(serializers.Serializer):
    target = serializers.ChoiceField(choices=AvailabilityStatus.choices)
