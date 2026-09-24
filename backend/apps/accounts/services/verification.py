"""Verification-code use cases.

Everything policy-bearing about OTP lives in this module and in
apps.accounts.models.verification: how long a code lives, how many attempts
are allowed, whether a previous code is invalidated on resend, and what a
successful verification does to the account.

The only delegated step is putting the code in front of the user.
"""

from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from core.api.exceptions import DomainError
from core.contracts.registry import verification_service
from core.contracts.verification import VerificationChannel, VerificationRequest
from core.security import generate_numeric_code

from apps.accounts.models import AccountStatus, User, VerificationCode, VerificationPurpose


class VerificationNotFoundError(DomainError):
    code = "verification_not_found"
    message = "No active verification code for this number."
    status_code = 404


class VerificationExpiredError(DomainError):
    code = "verification_expired"
    message = "This code has expired. Request a new one."


class VerificationAttemptsExceededError(DomainError):
    code = "verification_attempts_exceeded"
    message = "Too many incorrect attempts. Request a new code."


class VerificationCodeMismatchError(DomainError):
    code = "verification_code_mismatch"
    message = "The code is incorrect."


@transaction.atomic
def issue_code(
    *,
    destination: str,
    purpose: str = VerificationPurpose.PHONE_CONFIRMATION,
    user: User | None = None,
    channel: VerificationChannel = VerificationChannel.SMS,
) -> VerificationCode:
    """Generate, persist and dispatch a code.

    Issuing a new code consumes any outstanding one for the same destination
    and purpose, so exactly one code is valid at any moment.
    """
    VerificationCode.objects.for_destination(destination, purpose).usable().update(
        consumed_at=timezone.now()
    )

    clear_code = generate_numeric_code(settings.ACCOUNTS_OTP_CODE_LENGTH)
    record = VerificationCode(
        user=user,
        destination=destination,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(seconds=settings.ACCOUNTS_OTP_TTL_SECONDS),
        max_attempts=settings.ACCOUNTS_OTP_MAX_ATTEMPTS,
    )
    record.set_code(clear_code)
    record.save()

    # Delivery is a contract call. No provider is named anywhere in this app.
    transaction.on_commit(
        lambda: verification_service().dispatch(
            VerificationRequest(
                channel=channel,
                destination=destination,
                code=clear_code,
                purpose=purpose,
                ttl_seconds=settings.ACCOUNTS_OTP_TTL_SECONDS,
            )
        )
    )
    return record


@transaction.atomic
def verify_code(
    *,
    destination: str,
    code: str,
    purpose: str = VerificationPurpose.PHONE_CONFIRMATION,
) -> VerificationCode:
    """Check a submitted code and consume it on success."""
    record = (
        VerificationCode.objects.for_destination(destination, purpose)
        .filter(consumed_at__isnull=True)
        .order_by("-created_at")
        .select_for_update()
        .first()
    )
    if record is None:
        raise VerificationNotFoundError()
    if record.is_expired:
        raise VerificationExpiredError()
    if record.is_exhausted:
        raise VerificationAttemptsExceededError()

    if not record.matches(code):
        record.register_attempt()
        raise VerificationCodeMismatchError()

    record.consume()
    if purpose == VerificationPurpose.PHONE_CONFIRMATION:
        _mark_phone_verified(record)
    return record


def _mark_phone_verified(record: VerificationCode) -> None:
    user = record.user or User.objects.filter(phone_number=record.destination).first()
    if user is None:
        return
    user.phone_verified_at = timezone.now()
    if user.status == AccountStatus.PENDING:
        user.status = AccountStatus.ACTIVE
    user.save(update_fields=["phone_verified_at", "status", "updated_at"])
