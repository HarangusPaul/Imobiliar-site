import pytest
from django.core.exceptions import ValidationError

from core.validation import clamp_int, normalize_phone, unique_slugify


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("0721 234 567", "+40721234567"),
        ("+40 721-234-567", "+40721234567"),
        ("0040721234567", "+40721234567"),
        ("(0721) 234567", "+40721234567"),
    ],
)
def test_normalize_phone_produces_one_canonical_form(raw, expected):
    assert normalize_phone(raw) == expected


@pytest.mark.parametrize("raw", ["", "abc", "+0721", "12"])
def test_normalize_phone_rejects_invalid_input(raw):
    with pytest.raises(ValidationError):
        normalize_phone(raw)


def test_unique_slugify_appends_suffix_until_free():
    taken = {"garsoniera-centru", "garsoniera-centru-2"}
    assert unique_slugify("Garsonieră Centru", exists=taken.__contains__) == "garsoniera-centru-3"


def test_clamp_int_bounds_untrusted_input():
    assert clamp_int("500", minimum=1, maximum=100, default=24) == 100
    assert clamp_int("nope", minimum=1, maximum=100, default=24) == 24
