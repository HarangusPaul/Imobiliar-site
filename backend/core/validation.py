"""Domain-neutral validation helpers.

Everything here is about *format*, not about business meaning. Phone-number
normalisation lives here because it is a syntactic concern shared by accounts,
leads and contact forms; "a phone number must be unique per account" is an
``apps/accounts`` rule and is not implemented here.

Explicitly NOT in this module: price rules, area rules, lead-status rules,
OTP expiry.
"""

from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.utils.text import slugify as django_slugify

E164_RE = re.compile(r"^\+[1-9]\d{7,14}$")
_NON_DIGIT_RE = re.compile(r"[^\d+]")


def normalize_phone(raw: str, *, default_country_prefix: str = "+40") -> str:
    """Return a phone number in E.164 form or raise ``ValidationError``.

    Accepts the shapes users actually type (spaces, dashes, parentheses,
    ``00`` international prefix, national leading zero) and produces one
    canonical string. The canonical form is what ``apps/accounts`` stores as
    the unique login identifier, so normalisation must be deterministic.
    """
    if not raw:
        raise ValidationError("A phone number is required.", code="phone_required")

    cleaned = _NON_DIGIT_RE.sub("", raw.strip())

    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]
    elif cleaned.startswith("0"):
        cleaned = default_country_prefix + cleaned[1:]
    elif not cleaned.startswith("+"):
        cleaned = "+" + cleaned

    if not E164_RE.match(cleaned):
        raise ValidationError("Enter a valid phone number.", code="phone_invalid")
    return cleaned


def validate_phone(raw: str) -> None:
    """Field-level validator wrapper for model/serializer use."""
    normalize_phone(raw)


def unique_slugify(value: str, *, exists: "callable[[str], bool]", max_length: int = 255) -> str:
    """Build a URL slug, appending ``-2``, ``-3`` … until ``exists`` is False.

    The caller supplies the uniqueness probe, so ``core`` never touches a
    domain queryset.
    """
    base = django_slugify(unicodedata.normalize("NFKD", value))[:max_length] or "item"
    candidate = base
    suffix = 1
    while exists(candidate):
        suffix += 1
        tail = f"-{suffix}"
        candidate = f"{base[: max_length - len(tail)]}{tail}"
    return candidate


def parse_decimal(value: str | int | float | Decimal, *, field: str = "value") -> Decimal:
    """Coerce user input to ``Decimal`` with a predictable error."""
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError(f"Enter a valid number for {field}.", code="invalid_decimal") from exc


def ensure_non_negative(value: Decimal, *, field: str = "value") -> Decimal:
    """Reject negatives. Domain-neutral: says nothing about what a price means."""
    if value < 0:
        raise ValidationError(f"{field} cannot be negative.", code="negative_value")
    return value


def clamp_int(value: object, *, minimum: int, maximum: int, default: int) -> int:
    """Bound an untrusted integer query parameter. Used by selectors and filters."""
    try:
        parsed = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, parsed))
