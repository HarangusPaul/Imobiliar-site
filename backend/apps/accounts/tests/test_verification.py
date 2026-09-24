import pytest
from django.test import override_settings
from django.utils import timezone

from apps.accounts.models import AccountStatus, VerificationCode
from apps.accounts.services.registration import RegistrationInput, register_client
from apps.accounts.services.verification import (
    VerificationAttemptsExceededError,
    VerificationCodeMismatchError,
    VerificationExpiredError,
    issue_code,
    verify_code,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return register_client(RegistrationInput(phone_number="0721234567", password="correct-horse"))


def test_issuing_a_code_never_stores_it_in_clear(user):
    record = issue_code(destination=user.phone_number, user=user)
    assert record.code_hash and len(record.code_hash) == 64


def test_issuing_a_second_code_invalidates_the_first(user):
    first = issue_code(destination=user.phone_number, user=user)
    issue_code(destination=user.phone_number, user=user)
    first.refresh_from_db()
    assert first.consumed_at is not None


def test_expired_code_is_rejected(user, monkeypatch):
    record = issue_code(destination=user.phone_number, user=user)
    record.expires_at = timezone.now() - timezone.timedelta(seconds=1)
    record.save(update_fields=["expires_at"])
    with pytest.raises(VerificationExpiredError):
        verify_code(destination=user.phone_number, code="000000")


@override_settings(ACCOUNTS_OTP_MAX_ATTEMPTS=2)
def test_attempts_are_capped(user):
    issue_code(destination=user.phone_number, user=user)
    with pytest.raises(VerificationCodeMismatchError):
        verify_code(destination=user.phone_number, code="000000")
    with pytest.raises(VerificationCodeMismatchError):
        verify_code(destination=user.phone_number, code="000001")
    with pytest.raises(VerificationAttemptsExceededError):
        verify_code(destination=user.phone_number, code="000002")


def test_successful_verification_activates_the_account(user, capsys):
    # The console implementation logs the clear code; the domain never returns it.
    record = issue_code(destination=user.phone_number, user=user)
    clear = "111111"
    record.set_code(clear)
    record.save(update_fields=["code_hash"])

    verify_code(destination=user.phone_number, code=clear)

    user.refresh_from_db()
    assert user.status == AccountStatus.ACTIVE
    assert user.is_phone_verified
    assert VerificationCode.objects.get(pk=record.pk).consumed_at is not None
