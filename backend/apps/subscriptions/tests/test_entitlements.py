import pytest

from apps.accounts.services.registration import RegistrationInput, register_client
from apps.subscriptions.models import Entitlement, Plan
from apps.subscriptions.selectors.entitlements import effective_plan, has_entitlement
from apps.subscriptions.services.lifecycle import cancel_subscription, grant_subscription

pytestmark = pytest.mark.django_db


@pytest.fixture
def plans():
    free = Plan.objects.create(code="free", name="Free", is_default=True, entitlements=[])
    premium = Plan.objects.create(
        code="premium",
        name="Premium",
        entitlements=[Entitlement.PREMIUM_FILTERS, Entitlement.SUBSCRIBER_ONLY_FIELDS],
    )
    return free, premium


@pytest.fixture
def user():
    return register_client(RegistrationInput(phone_number="0721234567", password="correct-horse"))


def test_a_user_without_a_subscription_falls_back_to_the_default_plan(user, plans):
    free, _premium = plans
    assert effective_plan(user) == free
    assert not has_entitlement(user, Entitlement.PREMIUM_FILTERS)


def test_granting_premium_unlocks_its_entitlements(user, plans):
    grant_subscription(user=user, plan_code="premium")
    assert has_entitlement(user, Entitlement.PREMIUM_FILTERS)


def test_only_one_subscription_is_ever_current(user, plans):
    grant_subscription(user=user, plan_code="premium")
    grant_subscription(user=user, plan_code="free")
    assert user.subscriptions.count() == 2
    assert not has_entitlement(user, Entitlement.PREMIUM_FILTERS)


def test_cancelling_revokes_entitlements(user, plans):
    subscription = grant_subscription(user=user, plan_code="premium")
    cancel_subscription(subscription, immediate=True)
    assert not has_entitlement(user, Entitlement.PREMIUM_FILTERS)
