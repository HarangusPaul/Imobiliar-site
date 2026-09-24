"""Verification-code state.

This is the half of OTP that belongs to the domain: what code was issued, for
what purpose, when it expires, how many times it has been tried, and whether
it has been consumed. Delivery is somebody else's problem entirely - see
``core.contracts.verification``.

The model exists now, with no delivery channel configured, precisely so that
enabling SMS or WhatsApp later is a services change rather than an account
architecture change.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel
from core.security import hash_secret, secrets_match


class VerificationPurpose(models.TextChoices):
    PHONE_CONFIRMATION = "phone_confirmation", _("Phone confirmation")
    PASSWORD_RESET = "password_reset", _("Password reset")
    PHONE_CHANGE = "phone_change", _("Phone number change")


class VerificationCodeQuerySet(models.QuerySet):
    def usable(self) -> "VerificationCodeQuerySet":
        return self.filter(consumed_at__isnull=True, expires_at__gt=timezone.now())

    def for_destination(self, phone_number: str, purpose: str) -> "VerificationCodeQuerySet":
        return self.filter(destination=phone_number, purpose=purpose)


class VerificationCode(BaseModel):
    """A single issued code. The clear code is never stored."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification_codes",
        null=True,
        blank=True,
        help_text=_("Null while verifying a phone number that has no account yet."),
    )
    destination = models.CharField(max_length=20, db_index=True)
    purpose = models.CharField(max_length=32, choices=VerificationPurpose.choices)

    code_hash = models.CharField(max_length=64, editable=False)
    expires_at = models.DateTimeField(db_index=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=5)
    consumed_at = models.DateTimeField(null=True, blank=True)

    objects = VerificationCodeQuerySet.as_manager()

    class Meta:
        verbose_name = _("verification code")
        verbose_name_plural = _("verification codes")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["destination", "purpose", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.purpose} -> {self.destination}"

    # --- policy, owned here and nowhere else -------------------------------

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_exhausted(self) -> bool:
        return self.attempts >= self.max_attempts

    @property
    def is_usable(self) -> bool:
        return self.consumed_at is None and not self.is_expired and not self.is_exhausted

    def set_code(self, clear_code: str) -> None:
        self.code_hash = hash_secret(clear_code, salt=self._salt)

    def matches(self, candidate: str) -> bool:
        return secrets_match(candidate, self.code_hash, salt=self._salt)

    def register_attempt(self) -> None:
        self.attempts += 1
        self.save(update_fields=["attempts", "updated_at"])

    def consume(self) -> None:
        self.consumed_at = timezone.now()
        self.save(update_fields=["consumed_at", "updated_at"])

    @property
    def _salt(self) -> str:
        # Binding the hash to destination and purpose stops a code issued for
        # one flow from being replayed in another.
        return f"{self.purpose}:{self.destination}"
