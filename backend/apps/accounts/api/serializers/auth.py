"""Serializers for the authentication endpoints.

Serializers validate *shape*. Business outcomes (does this account exist, is
the password right, may this account hold a session) are decided by the
service layer, so a serializer never queries for a user to check credentials.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from core.validation import normalize_phone

from apps.accounts.models import User


class PhoneNumberField(serializers.CharField):
    """A phone number in any human format, stored in E.164."""

    def to_internal_value(self, data: object) -> str:
        value = super().to_internal_value(data)
        try:
            return normalize_phone(
                value, default_country_prefix=settings.ACCOUNTS_DEFAULT_PHONE_PREFIX
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc


class RegisterSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(max_length=24)
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)
    first_name = serializers.CharField(max_length=80, required=False, allow_blank=True, default="")
    last_name = serializers.CharField(max_length=80, required=False, allow_blank=True, default="")
    email = serializers.EmailField(required=False, allow_blank=True, default="")

    def validate_password(self, value: str) -> str:
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value


class LoginSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(max_length=24)
    password = serializers.CharField(write_only=True, max_length=128, trim_whitespace=False)
    remember = serializers.BooleanField(required=False, default=True)


class AccountSerializer(serializers.ModelSerializer):
    """The account as its owner sees it.

    ``roles`` is read through apps.access. It is exposed here because the
    frontend needs it on the session payload to choose a shell; the values
    themselves remain owned by that app.
    """

    id = serializers.UUIDField(source="uuid", read_only=True)
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "email",
            "status",
            "is_phone_verified",
            "roles",
            "created_at",
        ]
        read_only_fields = fields

    def get_roles(self, user: User) -> list[str]:
        from apps.access.selectors.roles import role_codes_for

        return role_codes_for(user)
