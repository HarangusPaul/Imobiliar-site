import pytest

from core.api.exceptions import ConflictError

from apps.accounts.models import AccountStatus, User
from apps.accounts.services.registration import RegistrationInput, register_client

pytestmark = pytest.mark.django_db


def test_register_normalizes_the_phone_number():
    user = register_client(RegistrationInput(phone_number="0721 234 567", password="correct-horse"))
    assert user.phone_number == "+40721234567"
    assert user.status == AccountStatus.PENDING
    assert not user.is_phone_verified


def test_register_rejects_a_duplicate_number_in_any_format():
    register_client(RegistrationInput(phone_number="+40721234567", password="correct-horse"))
    with pytest.raises(ConflictError):
        register_client(RegistrationInput(phone_number="0721234567", password="another-pass"))
    assert User.objects.count() == 1


def test_registered_user_receives_the_default_role():
    from apps.access.selectors.roles import role_codes_for

    user = register_client(RegistrationInput(phone_number="0721234567", password="correct-horse"))
    assert role_codes_for(user) == ["client"]
