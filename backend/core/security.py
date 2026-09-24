"""Generic security helpers.

Cryptographic and sanitisation primitives with no business meaning attached.
The *policy* that uses them (how long an OTP lives, how many attempts are
allowed) belongs to ``apps/accounts``.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

from django.conf import settings


def generate_numeric_code(length: int = 6) -> str:
    """Cryptographically strong numeric code (used for verification codes)."""
    if length < 4:
        raise ValueError("Numeric codes must be at least 4 digits.")
    return "".join(secrets.choice("0123456789") for _ in range(length))


def generate_token(nbytes: int = 32) -> str:
    """URL-safe opaque token (session handles, one-time links)."""
    return secrets.token_urlsafe(nbytes)


def hash_secret(value: str, *, salt: str = "") -> str:
    """Keyed hash for low-entropy secrets that must not be stored in clear.

    Uses the project ``SECRET_KEY`` as the HMAC key so a database leak alone
    does not reveal stored codes. Not a password hasher — use Django's
    ``make_password`` for passwords.
    """
    key = f"{settings.SECRET_KEY}{salt}".encode()
    return hmac.new(key, value.encode(), hashlib.sha256).hexdigest()


def secrets_match(candidate: str, hashed: str, *, salt: str = "") -> bool:
    """Constant-time comparison of a candidate against a stored hash."""
    return hmac.compare_digest(hash_secret(candidate, salt=salt), hashed)


def mask_phone(phone: str, *, visible: int = 3) -> str:
    """Mask a phone number for logs and for UI echo (``+4072*****89``)."""
    if len(phone) <= visible + 2:
        return "*" * len(phone)
    return f"{phone[:visible]}{'*' * (len(phone) - visible - 2)}{phone[-2:]}"
