"""Property-specific validation rules.

These are business rules and therefore live in the app, not in core. core
knows how to parse a decimal; only this module knows that a rental must carry
a rent period, or that a sale price below a floor is almost certainly a typo.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError

from apps.properties.models.enums import TransactionType

MIN_SALE_PRICE = Decimal("1000.00")
MIN_RENT_PRICE = Decimal("1.00")
MAX_PRICE = Decimal("999999999.99")
MAX_AREA = Decimal("1000000.00")


def validate_price(price: Decimal, *, transaction_type: str) -> None:
    """A price must be plausible for the kind of transaction.

    The floors exist to catch data-entry errors (a sale listed at 120 instead
    of 120000), which are far more common than genuinely cheap listings.
    """
    if price is None:
        raise ValidationError({"price": "A price is required."})
    if price > MAX_PRICE:
        raise ValidationError({"price": "This price is out of range."})

    floor = MIN_SALE_PRICE if transaction_type == TransactionType.SALE else MIN_RENT_PRICE
    if price < floor:
        raise ValidationError(
            {"price": f"A {transaction_type} price below {floor} looks like a data-entry error."}
        )


def validate_rent_period(rent_period: str, *, transaction_type: str) -> None:
    if transaction_type == TransactionType.RENT and not rent_period:
        raise ValidationError({"rent_period": "Rentals must state a rent period."})
    if transaction_type == TransactionType.SALE and rent_period:
        raise ValidationError({"rent_period": "Sales must not have a rent period."})


def validate_areas(usable_area: Decimal | None, total_area: Decimal | None) -> None:
    for name, value in (("usable_area", usable_area), ("total_area", total_area)):
        if value is not None and (value <= 0 or value > MAX_AREA):
            raise ValidationError({name: "This area is out of range."})

    if usable_area and total_area and usable_area > total_area:
        raise ValidationError(
            {"usable_area": "Usable area cannot exceed total area."}
        )


def validate_floors(floor: int | None, total_floors: int | None) -> None:
    if floor is not None and total_floors is not None and floor > total_floors:
        raise ValidationError({"floor": "The floor cannot be above the building height."})
