"""Project-wide pytest configuration.

Fixtures defined here are visible to every test package, which is why the
shared domain fixtures (an address, an agent, a staff member, a property
factory) live in one place rather than being redefined per app.
"""

from decimal import Decimal

import pytest

from core.contracts.registry import reset_providers


@pytest.fixture(autouse=True)
def _reset_service_providers():
    """Each test resolves service implementations afresh.

    Without this, a test that swaps an implementation would leak it into every
    later test through the registry cache.
    """
    reset_providers()
    yield
    reset_providers()


@pytest.fixture
def roles(db):
    from apps.access.services.assignment import ensure_system_roles

    ensure_system_roles()


@pytest.fixture
def agent(roles):
    from apps.access.services.assignment import assign_role
    from apps.accounts.services.registration import RegistrationInput, register_client

    user = register_client(RegistrationInput(phone_number="0721000001", password="correct-horse"))
    assign_role(user, code="agent")
    return user


@pytest.fixture
def staff(roles):
    from apps.access.services.assignment import assign_role
    from apps.accounts.services.registration import RegistrationInput, register_client

    user = register_client(RegistrationInput(phone_number="0721000002", password="correct-horse"))
    assign_role(user, code="staff")
    return user


@pytest.fixture
def address(db):
    from apps.locations.models import Address, City, Country, Neighborhood

    country = Country.objects.create(code="RO", name="Romania", phone_prefix="+40")
    city = City.objects.create(country=country, name="Cluj-Napoca", slug="cluj-napoca")
    Neighborhood.objects.create(city=city, name="Marasti", slug="marasti")
    return Address.objects.create(city=city, street="Strada Dorobantilor", street_number="14")


@pytest.fixture
def make_property(agent, address):
    from apps.properties.models import PropertyType, TransactionType
    from apps.properties.services.listing import PropertyInput, create_property

    def _make(**overrides):
        data = {
            "title": overrides.pop("title", "Two-room apartment"),
            "property_type": PropertyType.APARTMENT,
            "transaction_type": TransactionType.SALE,
            "address_id": address.pk,
            "price": Decimal("120000.00"),
            "short_description": "Bright two-room apartment.",
            "rooms": 2,
            "usable_area": Decimal("54.00"),
        }
        data.update(overrides)
        return create_property(PropertyInput(**data), actor=agent)

    return _make
