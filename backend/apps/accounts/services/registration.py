"""Registration use case.

A service function owns the *write workflow*: validation that spans models,
the transaction boundary, and the side effects that follow. API views call
these; they never orchestrate writes themselves.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings
from django.db import IntegrityError, transaction

from core.api.exceptions import ConflictError
from core.contracts.analytics import AnalyticsEvent
from core.contracts.registry import analytics_service
from core.validation import normalize_phone

from apps.accounts.models import AccountStatus, User


@dataclass(frozen=True, slots=True)
class RegistrationInput:
    phone_number: str
    password: str
    first_name: str = ""
    last_name: str = ""
    email: str = ""


@transaction.atomic
def register_client(data: RegistrationInput) -> User:
    """Create a client account.

    The new account starts as PENDING: it can log in today, and the same state
    becomes the awaiting-verification state once OTP is switched on. Role
    assignment is delegated to apps.access - this service does not define what
    a role is.
    """
    phone_number = normalize_phone(
        data.phone_number, default_country_prefix=settings.ACCOUNTS_DEFAULT_PHONE_PREFIX
    )

    try:
        user = User.objects.create_user(
            phone_number=phone_number,
            password=data.password,
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            email=data.email.strip().lower(),
            status=AccountStatus.PENDING,
        )
    except IntegrityError as exc:
        raise ConflictError("An account with this phone number already exists.") from exc

    _assign_default_role(user)

    analytics_service().track(AnalyticsEvent(name="account.registered", actor_id=str(user.uuid)))
    return user


def _assign_default_role(user: User) -> None:
    """Give the new account the default product role.

    Imported lazily so accounts has no import-time dependency on access; the
    two apps are peers and the edge is intentionally thin.
    """
    from apps.access.services.assignment import assign_default_role

    assign_default_role(user)
