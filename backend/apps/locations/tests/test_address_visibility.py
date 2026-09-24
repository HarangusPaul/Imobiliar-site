import pytest

from apps.locations.models import Address, City, Country, Neighborhood

pytestmark = pytest.mark.django_db


@pytest.fixture
def address():
    country = Country.objects.create(code="RO", name="Romania", phone_prefix="+40")
    city = City.objects.create(country=country, name="Cluj-Napoca", slug="cluj-napoca")
    neighborhood = Neighborhood.objects.create(city=city, name="Marasti", slug="marasti")
    return Address.objects.create(
        city=city,
        neighborhood=neighborhood,
        street="Strada Dorobantilor",
        street_number="14B",
        postal_code="400117",
    )


def test_public_label_hides_the_street_by_default(address):
    assert address.public_label == "Marasti, Cluj-Napoca"
    assert "Dorobantilor" not in address.public_label


def test_full_label_is_complete_for_internal_use(address):
    assert address.full_label == "Strada Dorobantilor 14B, Marasti, Cluj-Napoca"
