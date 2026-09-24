from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.properties.models import TransactionType
from apps.properties.validators import validate_areas, validate_price, validate_rent_period


def test_a_sale_price_that_looks_like_a_typo_is_rejected():
    with pytest.raises(ValidationError):
        validate_price(Decimal("120"), transaction_type=TransactionType.SALE)


def test_the_same_figure_is_fine_for_a_rental():
    validate_price(Decimal("120"), transaction_type=TransactionType.RENT)


def test_rentals_require_a_rent_period():
    with pytest.raises(ValidationError):
        validate_rent_period("", transaction_type=TransactionType.RENT)


def test_sales_must_not_carry_a_rent_period():
    with pytest.raises(ValidationError):
        validate_rent_period("month", transaction_type=TransactionType.SALE)


def test_usable_area_cannot_exceed_total_area():
    with pytest.raises(ValidationError):
        validate_areas(Decimal("120"), Decimal("80"))
