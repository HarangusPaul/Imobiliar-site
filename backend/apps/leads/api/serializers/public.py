"""Public lead submission serializer.

Accepts a property or development by its *public* identifier (slug), never by
database id, and resolves it here so the service receives a real relation.
"""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from core.validation import normalize_phone

from apps.developments.models import Development
from apps.leads.models import ContactPreference, LeadKind
from apps.properties.models import Property


class LeadSubmissionSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=160)
    phone_number = serializers.CharField(max_length=24)
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    message = serializers.CharField(
        max_length=4000, required=False, allow_blank=True, default=""
    )

    kind = serializers.ChoiceField(choices=LeadKind.choices, default=LeadKind.GENERAL)
    contact_preference = serializers.ChoiceField(
        choices=ContactPreference.choices, default=ContactPreference.ANY
    )
    preferred_time = serializers.CharField(
        max_length=120, required=False, allow_blank=True, default=""
    )

    property_slug = serializers.SlugField(required=False, allow_blank=True, default="")
    development_slug = serializers.SlugField(required=False, allow_blank=True, default="")
    source_path = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )

    # Honeypot: a real browser leaves it empty, most naive bots fill it.
    website = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_phone_number(self, value: str) -> str:
        try:
            return normalize_phone(
                value, default_country_prefix=settings.ACCOUNTS_DEFAULT_PHONE_PREFIX
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc

    def validate(self, attrs: dict) -> dict:
        if attrs.pop("website", ""):
            raise serializers.ValidationError("This submission was rejected.")

        property_slug = attrs.pop("property_slug", "")
        development_slug = attrs.pop("development_slug", "")

        attrs["property_id"] = None
        attrs["development_id"] = None

        if property_slug:
            prop = Property.objects.published().filter(slug=property_slug).only("id").first()
            if prop is None:
                raise serializers.ValidationError({"property_slug": "Unknown listing."})
            attrs["property_id"] = prop.pk
            attrs.setdefault("kind", LeadKind.PROPERTY)

        if development_slug:
            development = (
                Development.objects.published().filter(slug=development_slug).only("id").first()
            )
            if development is None:
                raise serializers.ValidationError({"development_slug": "Unknown development."})
            attrs["development_id"] = development.pk

        if not attrs.get("message") and not attrs["property_id"] and not attrs["development_id"]:
            raise serializers.ValidationError(
                {"message": "Tell us what you are looking for."}
            )
        return attrs


class LeadReceiptSerializer(serializers.Serializer):
    """What the website gets back. Deliberately minimal.

    A public endpoint must not echo internal state such as who the lead was
    assigned to.
    """

    id = serializers.UUIDField(source="uuid", read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
