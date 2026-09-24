"""Authentication backend keyed on the phone number.

Normalising the submitted identifier here means a user can type
``0721 234 567`` or ``+40721234567`` and reach the same account.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from django.http import HttpRequest

from core.validation import normalize_phone


class PhoneNumberBackend(ModelBackend):
    def authenticate(
        self,
        request: HttpRequest | None,
        username: str | None = None,
        password: str | None = None,
        **kwargs,
    ):
        User = get_user_model()
        identifier = kwargs.get("phone_number") or username
        if not identifier or not password:
            return None

        try:
            phone_number = normalize_phone(
                identifier, default_country_prefix=settings.ACCOUNTS_DEFAULT_PHONE_PREFIX
            )
        except ValidationError:
            # Run the hasher anyway so an invalid format is not distinguishable
            # by response time from a wrong password.
            User().set_password(password)
            return None

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            User().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def user_can_authenticate(self, user) -> bool:
        return bool(getattr(user, "can_authenticate", False))
