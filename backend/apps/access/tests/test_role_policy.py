import pytest

from apps.access.models import Role
from apps.access.policy import Capability
from apps.access.selectors.roles import can_reach_area, capabilities_for, has_capability
from apps.access.services.assignment import assign_role, ensure_system_roles, revoke_role
from apps.accounts.services.registration import RegistrationInput, register_client

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return register_client(RegistrationInput(phone_number="0721234567", password="correct-horse"))


def test_seeding_is_idempotent():
    ensure_system_roles()
    ensure_system_roles()
    assert Role.objects.filter(is_system=True).count() == 3


def test_client_cannot_reach_the_dashboard(user):
    assert can_reach_area(user, "client")
    assert not can_reach_area(user, "dashboard")


def test_capabilities_are_the_union_of_assigned_roles(user):
    assign_role(user, code="agent")
    granted = capabilities_for(user)
    assert Capability.PROPERTY_CREATE in granted
    assert Capability.PROPERTY_PUBLISH not in granted

    assign_role(user, code="staff")
    assert has_capability(user, Capability.PROPERTY_PUBLISH)

    revoke_role(user, code="staff")
    assert not has_capability(user, Capability.PROPERTY_PUBLISH)


def test_a_new_role_needs_no_code_change():
    """The point of roles-as-data: adding one is a row, not a branch."""
    ensure_system_roles()
    partner = Role.objects.create(
        code="partner_agency",
        name="Partner agency",
        areas=["public", "dashboard"],
        permissions=[Capability.PROPERTY_CREATE, Capability.LEAD_VIEW_OWN],
        priority=250,
    )
    user = register_client(RegistrationInput(phone_number="0722000000", password="correct-horse"))
    assign_role(user, code=partner.code)
    assert has_capability(user, Capability.PROPERTY_CREATE)
    assert can_reach_area(user, "dashboard")
