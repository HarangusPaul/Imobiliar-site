"""Deferred work owned by the accounts domain."""

from __future__ import annotations

from django.utils import timezone

from core.tasks import Task

from apps.accounts.models import VerificationCode


class PurgeExpiredVerificationCodesTask(Task):
    """Drop verification codes that can no longer be used.

    Retention is an accounts decision: consumed or expired codes carry no
    further business meaning, and keeping hashed codes around indefinitely is
    pointless risk.
    """

    name = "accounts.purge_expired_verification_codes"

    def run(self, *, older_than_days: int = 7) -> None:
        cutoff = timezone.now() - timezone.timedelta(days=older_than_days)
        VerificationCode.objects.filter(created_at__lt=cutoff).delete()


purge_expired_verification_codes = PurgeExpiredVerificationCodesTask()
