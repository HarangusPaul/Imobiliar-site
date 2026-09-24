"""Login and logout use cases."""

from __future__ import annotations

import logging

from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest

from core.api.exceptions import DomainError
from core.contracts.analytics import AnalyticsEvent
from core.contracts.registry import analytics_service
from core.security import mask_phone

from apps.accounts.models import User

logger = logging.getLogger(__name__)


class InvalidCredentialsError(DomainError):
    code = "invalid_credentials"
    message = "The phone number or password is incorrect."
    status_code = 400


def login_with_password(request: HttpRequest, *, phone_number: str, password: str) -> User:
    """Authenticate and open a session.

    One error covers every failure mode on purpose: a caller must not be able
    to distinguish an unknown account from a wrong password.
    """
    user = authenticate(request, username=phone_number, password=password)
    if user is None:
        logger.info("auth.login.failed phone=%s", mask_phone(phone_number))
        raise InvalidCredentialsError()

    login(request, user)
    analytics_service().track(AnalyticsEvent(name="account.logged_in", actor_id=str(user.uuid)))
    return user


def logout_session(request: HttpRequest) -> None:
    logout(request)
